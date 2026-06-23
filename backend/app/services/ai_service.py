from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import math
import pickle
from pathlib import Path
from typing import Any, List

from ..ml_model import RiskModel
from ..schemas import AtRiskPredictionItem, PredictionAtmFeatures, PredictionRequest, PredictionResponse, RecommendationItem, TopCriticalATM
from ..store import agencies, atms, cities, incidents
from .data_loader import ensure_data_loaded

model = RiskModel()

MODEL_DIR = Path(__file__).resolve().parents[2] / 'ml_artifacts'
MODEL_PATH = MODEL_DIR / 'gab_failure_random_forest.joblib'
PICKLE_FALLBACK_PATH = MODEL_DIR / 'gab_failure_random_forest.pkl'

FEATURE_COLUMNS = [
    'total_incidents',
    'incidents_7d',
    'incidents_30d',
    'incidents_90d',
    'monthly_frequency',
    'mttr_gab',
    'incidents_weekend',
    'incidents_semaine',
    'ratio_weekend',
    'incidents_lundi',
    'incidents_mardi',
    'incidents_mercredi',
    'incidents_jeudi',
    'incidents_vendredi',
    'incidents_samedi',
    'incidents_dimanche',
    'atm_age',
    'population',
    'pct_over60',
    'transaction_volume',
    'category_code',
    'motif_code',
    'type_code',
    'city_code',
    'agency_code',
    'critical_day_code',
]

failure_artifact: dict[str, Any] | None = None

DAY_LABELS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
DAY_FEATURES = [
    ('incidents_lundi', 'Lundi'),
    ('incidents_mardi', 'Mardi'),
    ('incidents_mercredi', 'Mercredi'),
    ('incidents_jeudi', 'Jeudi'),
    ('incidents_vendredi', 'Vendredi'),
    ('incidents_samedi', 'Samedi'),
    ('incidents_dimanche', 'Dimanche'),
]


def train_model() -> None:
    model.train()
    _train_failure_model()


def get_model_metrics() -> dict[str, Any]:
    artifact = _get_failure_artifact()
    return artifact.get('metrics', {}) if artifact else {}


def _risk_category(score: float) -> str:
    if score >= 80:
        return 'Critique'
    if score >= 60:
        return 'Élevé'
    if score >= 40:
        return 'Moyen'
    return 'Faible'


def _category_weight(category: str) -> float:
    normalized = category.strip().lower()
    if 'hardware' in normalized:
        return 100
    if 'communication' in normalized or 'réseau' in normalized or 'reseau' in normalized:
        return 82
    if 'software' in normalized or 'logiciel' in normalized:
        return 72
    if 'cash' in normalized or 'alimentation' in normalized:
        return 68
    return 50


def _safe_ratio(value: float, maximum: float) -> float:
    return value / maximum if maximum else 0.0


def _month_start(value: datetime) -> datetime:
    return datetime(value.year, value.month, 1)


def _next_month(value: datetime) -> datetime:
    return datetime(value.year + 1, 1, 1) if value.month == 12 else datetime(value.year, value.month + 1, 1)


def _month_end(value: datetime) -> datetime:
    return _next_month(value) - timedelta(seconds=1)


def _percentile(values: list[int], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return float(ordered[int(index)])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def _encode(value: str, encoder: dict[str, int]) -> int:
    key = value.strip().lower() or 'inconnu'
    if key not in encoder:
        encoder[key] = len(encoder) + 1
    return encoder[key]


def _city_for_agency(agency_name: str) -> str:
    agency = next((item for item in agencies if item['name'] == agency_name), None)
    return agency['city'] if agency else ''


def _city_context(city_name: str) -> tuple[int, float]:
    city = next((item for item in cities if item['name'].lower() == city_name.lower()), None)
    if not city:
        return 0, 0.0
    return int(city.get('population', 0)), float(city.get('pctOver60', 0.0))


def _dominant(values: list[str], fallback: str = 'Non renseigné') -> str:
    cleaned = [value for value in values if value]
    return Counter(cleaned).most_common(1)[0][0] if cleaned else fallback


def _temporal_features(history: list[dict[str, Any]]) -> dict[str, Any]:
    total_incidents = len(history)
    durations = [float(item.get('duration_min') or 0.0) for item in history]
    mttr_gab = sum(durations) / total_incidents if total_incidents else 0.0
    weekday_counts = {label: 0 for label in DAY_LABELS}

    for item in history:
        reported_at = item.get('reported_at')
        if not isinstance(reported_at, datetime):
            continue
        weekday_counts[DAY_LABELS[reported_at.weekday()]] += 1

    incidents_weekend = weekday_counts['Samedi'] + weekday_counts['Dimanche']
    incidents_semaine = total_incidents - incidents_weekend
    jour_plus_critique = max(weekday_counts, key=weekday_counts.get) if total_incidents else 'Non renseigné'

    # Variables métier temporelles calculées par GAB depuis l'historique incidents réel.
    return {
        'total_incidents': float(total_incidents),
        'mttr_gab': float(mttr_gab),
        'incidents_weekend': float(incidents_weekend),
        'incidents_semaine': float(incidents_semaine),
        'ratio_weekend': float(incidents_weekend / total_incidents) if total_incidents else 0.0,
        'jour_plus_critique': jour_plus_critique,
        'incidents_lundi': float(weekday_counts['Lundi']),
        'incidents_mardi': float(weekday_counts['Mardi']),
        'incidents_mercredi': float(weekday_counts['Mercredi']),
        'incidents_jeudi': float(weekday_counts['Jeudi']),
        'incidents_vendredi': float(weekday_counts['Vendredi']),
        'incidents_samedi': float(weekday_counts['Samedi']),
        'incidents_dimanche': float(weekday_counts['Dimanche']),
    }


def _build_feature_record(
    atm_serial: str,
    history: list[dict[str, Any]],
    cutoff: datetime,
    encoders: dict[str, dict[str, int]],
) -> dict[str, Any]:
    atm_info = next((item for item in atms if item['serial'] == atm_serial), None)
    agency_name = atm_info['agency'] if atm_info else (history[0]['agency'] if history else '')
    city_name = _city_for_agency(agency_name) or (history[0]['city'] if history else '')
    population, pct_over60 = _city_context(city_name)
    categories = [item.get('category', '') for item in history]
    motifs = [item.get('motif', '') for item in history]
    dominant_category = _dominant(categories, 'Non classé')
    dominant_motif = _dominant(motifs)
    type_gab = atm_info.get('type', '') if atm_info else ''
    first_month = min((_month_start(item['reported_at']) for item in history), default=_month_start(cutoff))
    observed_months = max(1, (cutoff.year - first_month.year) * 12 + cutoff.month - first_month.month + 1)

    # Features temporelles construites uniquement avec l'historique disponible avant le mois à prédire.
    incidents_7d = sum(1 for item in history if cutoff - timedelta(days=7) <= item['reported_at'] <= cutoff)
    incidents_30d = sum(1 for item in history if cutoff - timedelta(days=30) <= item['reported_at'] <= cutoff)
    incidents_90d = sum(1 for item in history if cutoff - timedelta(days=90) <= item['reported_at'] <= cutoff)
    monthly_frequency = len(history) / observed_months
    temporal = _temporal_features(history)

    # Les transactions réelles par GAB ne sont pas disponibles: on conserve une estimation transparente,
    # cohérente avec la charge historique et le contexte démographique.
    estimated_transactions = 1200 + monthly_frequency * 180 + population / 1500

    return {
        'atm': atm_serial,
        'agency': agency_name,
        'city': city_name,
        'dominantCategory': dominant_category,
        'dominantMotif': dominant_motif,
        'typeGab': type_gab,
        **temporal,
        'incidents_7d': float(incidents_7d),
        'incidents_30d': float(incidents_30d),
        'incidents_90d': float(incidents_90d),
        'monthly_frequency': float(monthly_frequency),
        'atm_age': float(max(1, cutoff.year - int(atm_info.get('year_installed', 2020)))) if atm_info else 5.0,
        'population': float(population),
        'pct_over60': float(pct_over60),
        'transaction_volume': float(estimated_transactions),
        'category_code': float(_encode(dominant_category, encoders['category'])),
        'motif_code': float(_encode(dominant_motif, encoders['motif'])),
        'type_code': float(_encode(type_gab, encoders['type'])),
        'city_code': float(_encode(city_name, encoders['city'])),
        'agency_code': float(_encode(agency_name, encoders['agency'])),
        'critical_day_code': float(_encode(temporal['jour_plus_critique'], encoders.setdefault('critical_day', {}))),
    }


def _build_training_dataset() -> tuple[list[dict[str, Any]], list[int], dict[str, dict[str, int]], float]:
    ensure_data_loaded()
    if not incidents:
        return [], [], {}, 0.0

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for incident in incidents:
        grouped[incident['atm']].append(incident)

    months = sorted({_month_start(item['reported_at']) for item in incidents})
    encoders = {'category': {}, 'motif': {}, 'type': {}, 'city': {}, 'agency': {}, 'critical_day': {}}
    rows: list[dict[str, Any]] = []
    targets: list[int] = []
    thresholds: list[float] = []

    for month in months[:-1]:
        next_month = _next_month(month)
        next_month_end = _month_end(next_month)
        next_counts = [
            sum(1 for item in atm_incidents if next_month <= item['reported_at'] <= next_month_end)
            for atm_incidents in grouped.values()
        ]
        positive_counts = [count for count in next_counts if count > 0]
        monthly_threshold = max(3.0, _percentile(positive_counts, 0.75))
        thresholds.append(monthly_threshold)
        cutoff = _month_end(month)

        for atm_serial, atm_incidents in grouped.items():
            history = [item for item in atm_incidents if item['reported_at'] <= cutoff]
            if not history:
                continue
            next_count = sum(1 for item in atm_incidents if next_month <= item['reported_at'] <= next_month_end)
            # Target métier: 1 si le GAB dépasse le seuil critique observé au mois suivant.
            targets.append(1 if next_count >= monthly_threshold else 0)
            rows.append(_build_feature_record(atm_serial, history, cutoff, encoders))

    return rows, targets, encoders, round(sum(thresholds) / len(thresholds), 2) if thresholds else 0.0


def _matrix(rows: list[dict[str, Any]]) -> list[list[float]]:
    return [[float(row[column]) for column in FEATURE_COLUMNS] for row in rows]


def _train_lightweight_logistic(x_train: list[list[float]], y_train: list[int]) -> dict[str, Any] | None:
    if not x_train or len(set(y_train)) < 2:
        return None

    feature_count = len(x_train[0])
    means = [sum(row[index] for row in x_train) / len(x_train) for index in range(feature_count)]
    stds = []
    for index in range(feature_count):
        variance = sum((row[index] - means[index]) ** 2 for row in x_train) / len(x_train)
        stds.append(math.sqrt(variance) or 1.0)

    scaled = [[(row[index] - means[index]) / stds[index] for index in range(feature_count)] for row in x_train]
    weights = [0.0 for _ in range(feature_count)]
    bias = 0.0
    learning_rate = 0.06

    for _ in range(1000):
        gradients = [0.0 for _ in range(feature_count)]
        bias_gradient = 0.0
        for row, target in zip(scaled, y_train):
            z_value = bias + sum(weight * value for weight, value in zip(weights, row))
            prediction = 1 / (1 + math.exp(-max(min(z_value, 35), -35)))
            error = prediction - target
            for index, value in enumerate(row):
                gradients[index] += error * value
            bias_gradient += error
        sample_count = len(scaled)
        weights = [weight - learning_rate * gradient / sample_count for weight, gradient in zip(weights, gradients)]
        bias -= learning_rate * bias_gradient / sample_count

    return {'kind': 'lightweight_logistic', 'weights': weights, 'bias': bias, 'means': means, 'stds': stds}


def _evaluate_predictions(y_true: list[int], probabilities: list[float]) -> dict[str, float]:
    if not y_true:
        return {}
    predicted = [1 if probability >= 0.5 else 0 for probability in probabilities]
    tp = sum(1 for truth, pred in zip(y_true, predicted) if truth == 1 and pred == 1)
    tn = sum(1 for truth, pred in zip(y_true, predicted) if truth == 0 and pred == 0)
    fp = sum(1 for truth, pred in zip(y_true, predicted) if truth == 0 and pred == 1)
    fn = sum(1 for truth, pred in zip(y_true, predicted) if truth == 1 and pred == 0)
    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    metrics = {
        'accuracy': round(accuracy, 3),
        'precision': round(precision, 3),
        'recall': round(recall, 3),
        'f1Score': round(f1, 3),
    }
    try:
        from sklearn.metrics import roc_auc_score

        if len(set(y_true)) > 1:
            metrics['rocAuc'] = round(float(roc_auc_score(y_true, probabilities)), 3)
    except Exception:
        pass
    return metrics


def _predict_probability_from_artifact(artifact: dict[str, Any], feature_values: list[float]) -> float:
    trained_model = artifact.get('model')
    if trained_model is not None and hasattr(trained_model, 'predict_proba'):
        return float(trained_model.predict_proba([feature_values])[0][1])

    if trained_model is not None and hasattr(trained_model, 'predict'):
        raw_prediction = trained_model.predict([feature_values])[0]
        return float(max(0, min(1, raw_prediction)))

    if artifact.get('kind') == 'lightweight_logistic':
        means = artifact['means']
        stds = artifact['stds']
        scaled = [(value - means[index]) / stds[index] for index, value in enumerate(feature_values)]
        z_value = artifact['bias'] + sum(weight * value for weight, value in zip(artifact['weights'], scaled))
        return 1 / (1 + math.exp(-max(min(z_value, 35), -35)))

    return 0.0


def _persist_artifact(artifact: dict[str, Any]) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import joblib

        joblib.dump(artifact, MODEL_PATH)
    except Exception:
        with PICKLE_FALLBACK_PATH.open('wb') as file:
            pickle.dump(artifact, file)


def _load_persisted_artifact() -> dict[str, Any] | None:
    try:
        if MODEL_PATH.exists():
            import joblib

            return joblib.load(MODEL_PATH)
    except Exception:
        pass
    try:
        if PICKLE_FALLBACK_PATH.exists():
            with PICKLE_FALLBACK_PATH.open('rb') as file:
                return pickle.load(file)
    except Exception:
        pass
    return None


def _train_failure_model() -> dict[str, Any] | None:
    global failure_artifact
    rows, targets, encoders, target_threshold = _build_training_dataset()
    if len(rows) < 20 or len(set(targets)) < 2:
        failure_artifact = None
        return None

    split_index = max(1, int(len(rows) * 0.8))
    x_train = _matrix(rows[:split_index])
    y_train = targets[:split_index]
    x_test = _matrix(rows[split_index:]) or x_train
    y_test = targets[split_index:] or y_train

    trained_model: Any = None
    kind = 'lightweight_logistic'

    try:
        from sklearn.ensemble import RandomForestClassifier

        # Modèle principal demandé: Random Forest, adapté aux variables mixtes et robuste sur peu de données.
        trained_model = RandomForestClassifier(
            n_estimators=180,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced',
        )
        trained_model.fit(x_train, y_train)
        kind = 'random_forest'
    except Exception:
        trained_model = _train_lightweight_logistic(x_train, y_train)

    probabilities = [_predict_probability_from_artifact({'model': trained_model, 'kind': kind, **(trained_model or {})} if isinstance(trained_model, dict) else {'model': trained_model, 'kind': kind}, row) for row in x_test]
    metrics = _evaluate_predictions(y_test, probabilities)

    if isinstance(trained_model, dict):
        artifact = {
            **trained_model,
            'model': None,
            'featureColumns': FEATURE_COLUMNS,
            'encoders': encoders,
            'metrics': metrics,
            'targetThreshold': target_threshold,
            'trainedAt': datetime.now().isoformat(timespec='seconds'),
        }
    else:
        artifact = {
            'kind': kind,
            'model': trained_model,
            'featureColumns': FEATURE_COLUMNS,
            'encoders': encoders,
            'metrics': metrics,
            'targetThreshold': target_threshold,
            'trainedAt': datetime.now().isoformat(timespec='seconds'),
        }

    failure_artifact = artifact
    _persist_artifact(artifact)
    return artifact


def _get_failure_artifact() -> dict[str, Any] | None:
    global failure_artifact
    ensure_data_loaded()
    if failure_artifact is not None:
        if failure_artifact.get('featureColumns') != FEATURE_COLUMNS:
            failure_artifact = None
            return _train_failure_model()
        return failure_artifact
    failure_artifact = _load_persisted_artifact()
    if failure_artifact is not None:
        if failure_artifact.get('featureColumns') != FEATURE_COLUMNS:
            failure_artifact = None
            return _train_failure_model()
        return failure_artifact
    return _train_failure_model()


def _feature_record_from_atm_code(
    atm_code: str,
    encoders: dict[str, dict[str, int]],
    transaction_volume: float | None = None,
) -> dict[str, Any] | None:
    ensure_data_loaded()
    atm_incidents = [incident for incident in incidents if incident['atm'] == atm_code]
    if not atm_incidents:
        return None

    cutoff = max(incident['reported_at'] for incident in incidents)
    feature_record = _build_feature_record(atm_code, atm_incidents, cutoff, encoders)
    if transaction_volume and transaction_volume > 0:
        feature_record['transaction_volume'] = float(transaction_volume)
    return feature_record


def _request_features(request: PredictionRequest, encoders: dict[str, dict[str, int]]) -> dict[str, Any]:
    # Si le formulaire transmet un vrai Code GAB, on reconstruit les features depuis l'historique réel.
    # Les valeurs envoyées par le frontend servent surtout à afficher/contrôler le formulaire.
    if request.atmCode:
        atm_features = _feature_record_from_atm_code(request.atmCode, encoders, request.transactionVolume)
        if atm_features:
            return atm_features

    # Fallback: utile si le formulaire est appelé sans GAB ou si une donnée historique manque.
    incident_count = max(0, request.incidentCount)
    incidents_7d = request.incidents7d if request.incidents7d is not None else round(incident_count / 4, 2)
    incidents_30d = request.incidents30d if request.incidents30d is not None else incident_count
    incidents_90d = request.incidents90d if request.incidents90d is not None else incident_count * 3
    monthly_frequency = request.monthlyFrequency if request.monthlyFrequency is not None else incident_count
    incidents_weekend = request.incidentsWeekend if request.incidentsWeekend is not None else 0
    incidents_semaine = request.incidentsSemaine if request.incidentsSemaine is not None else incident_count
    total_incidents = incidents_weekend + incidents_semaine if incidents_weekend + incidents_semaine else incident_count
    ratio_weekend = request.ratioWeekend if request.ratioWeekend is not None else (incidents_weekend / total_incidents if total_incidents else 0.0)
    jour_plus_critique = request.jourPlusCritique or 'Non renseigné'
    return {
        'atm': request.atmCode or '',
        'agency': request.agency or '',
        'city': request.city or '',
        'dominantCategory': request.dominantCategory or 'Non classé',
        'dominantMotif': request.dominantMotif or 'Non renseigné',
        'typeGab': request.typeGab or '',
        'total_incidents': float(total_incidents),
        'incidents_7d': float(incidents_7d),
        'incidents_30d': float(incidents_30d),
        'incidents_90d': float(incidents_90d),
        'monthly_frequency': float(monthly_frequency),
        'mttr_gab': float(request.mttrGab or 0.0),
        'incidents_weekend': float(incidents_weekend),
        'incidents_semaine': float(incidents_semaine),
        'ratio_weekend': float(ratio_weekend),
        'jour_plus_critique': jour_plus_critique,
        'incidents_lundi': 0.0,
        'incidents_mardi': 0.0,
        'incidents_mercredi': 0.0,
        'incidents_jeudi': 0.0,
        'incidents_vendredi': 0.0,
        'incidents_samedi': float(incidents_weekend),
        'incidents_dimanche': 0.0,
        'atm_age': float(request.atmAge),
        'population': float(request.population),
        'pct_over60': float(request.pctOver60),
        'transaction_volume': float(request.transactionVolume),
        'category_code': float(_encode(request.dominantCategory or 'Non classé', encoders.setdefault('category', {}))),
        'motif_code': float(_encode(request.dominantMotif or 'Non renseigné', encoders.setdefault('motif', {}))),
        'type_code': float(_encode(request.typeGab or 'Inconnu', encoders.setdefault('type', {}))),
        'city_code': float(_encode(request.city or 'Inconnu', encoders.setdefault('city', {}))),
        'agency_code': float(_encode(request.agency or 'Inconnu', encoders.setdefault('agency', {}))),
        'critical_day_code': float(_encode(jour_plus_critique, encoders.setdefault('critical_day', {}))),
    }


def _max_weekday_incidents(features: dict[str, Any]) -> float:
    return max(float(features.get(key, 0.0)) for key, _ in DAY_FEATURES)


def _score_from_probability_and_features(probability: float, features: dict[str, Any]) -> float:
    temporal_score = (
        min(float(features.get('total_incidents', 0.0)) / 90, 1) * 10
        + min(float(features.get('mttr_gab', 0.0)) / 240, 1) * 10
        + min(float(features.get('ratio_weekend', 0.0)) / 0.35, 1) * 8
        + min(_max_weekday_incidents(features) / 30, 1) * 7
    )
    model_score = probability * 65
    return round(min(100, max(0, model_score + temporal_score)), 1)


def _recommendation_for_features(risk_category: str, features: dict[str, Any]) -> str:
    if float(features.get('mttr_gab', 0.0)) >= 120:
        return 'Prioriser une analyse des délais d’intervention pour réduire le temps moyen de résolution.'
    if float(features.get('ratio_weekend', 0.0)) >= 0.25:
        return 'Prévoir une surveillance renforcée pendant le weekend.'
    critical_day = str(features.get('jour_plus_critique', '') or '')
    if critical_day and critical_day != 'Non renseigné':
        return f'Planifier une maintenance préventive avant le jour le plus critique: {critical_day}.'
    if risk_category == 'Critique':
        return 'Planifier une intervention préventive prioritaire.'
    if risk_category == 'Élevé':
        return 'Programmer un contrôle technique renforcé.'
    return 'Maintenir la surveillance préventive.'


def _temporal_response_fields(features: dict[str, Any]) -> dict[str, Any]:
    return {
        'mttrGab': round(float(features.get('mttr_gab', 0.0)), 1),
        'incidentsWeekend': int(round(float(features.get('incidents_weekend', 0.0)))),
        'incidentsSemaine': int(round(float(features.get('incidents_semaine', 0.0)))),
        'ratioWeekend': round(float(features.get('ratio_weekend', 0.0)), 3),
        'jourPlusCritique': str(features.get('jour_plus_critique', 'Non renseigné') or 'Non renseigné'),
    }


def _prediction_explanation(request: PredictionRequest, probability: float, features: dict[str, Any]) -> str:
    reasons = []
    recent_incidents = request.incidents30d if request.incidents30d is not None else request.incidentCount
    if recent_incidents >= 8:
        reasons.append('nombre important d’incidents récents')
    elif recent_incidents >= 4:
        reasons.append('historique récent significatif')
    if request.transactionVolume >= 3000:
        reasons.append('volume transactionnel élevé')
    if request.pctOver60 >= 15:
        reasons.append('contexte démographique sensible')
    if request.atmAge >= 6:
        reasons.append('âge du GAB supérieur à la moyenne')
    if float(features.get('mttr_gab', 0.0)) >= 120:
        reasons.append('MTTR élevé sur ce GAB')
    if float(features.get('ratio_weekend', 0.0)) >= 0.25:
        reasons.append('part importante d’incidents pendant le weekend')
    critical_day = str(features.get('jour_plus_critique', '') or '')
    if critical_day and critical_day != 'Non renseigné':
        reasons.append(f'concentration des incidents le {critical_day}')
    if not reasons:
        reasons.append('paramètres saisis modérés')
    return f"Le risque est estimé à {round(probability * 100, 1)}% à cause du " + ', '.join(reasons) + '.'


def predict_failure_risk(request: PredictionRequest) -> PredictionResponse:
    artifact = _get_failure_artifact()
    if artifact is None:
        raise ValueError('Modèle IA indisponible: données insuffisantes pour entraîner une cible mois suivant.')

    features = _request_features(request, artifact.get('encoders', {}))
    feature_values = [float(features[column]) for column in FEATURE_COLUMNS]
    probability = _predict_probability_from_artifact(artifact, feature_values)
    risk_score = _score_from_probability_and_features(probability, features)
    risk_category = _risk_category(risk_score)
    recommendation = _recommendation_for_features(risk_category, features)

    return PredictionResponse(
        atmCode=features.get('atm') or request.atmCode,
        agency=features.get('agency') or request.agency,
        city=features.get('city') or request.city,
        riskScore=risk_score,
        failureProbability=risk_score,
        riskCategory=risk_category,
        recommendation=recommendation,
        explanation=_prediction_explanation(request, probability, features),
        dominantMotif=features.get('dominantMotif', 'Non renseigné'),
        dominantCategory=features.get('dominantCategory', 'Non classé'),
        **_temporal_response_fields(features),
    )


def get_prediction_atms() -> list[PredictionAtmFeatures]:
    rows = _latest_rows_for_atms()
    return [
        PredictionAtmFeatures(
            atmCode=row['atm'],
            agency=row['agency'],
            city=row['city'],
            typeGab=row['typeGab'] or 'Non renseigné',
            dominantCategory=row['dominantCategory'],
            dominantMotif=row['dominantMotif'],
            incidents7d=round(float(row['incidents_7d']), 1),
            incidents30d=round(float(row['incidents_30d']), 1),
            incidents90d=round(float(row['incidents_90d']), 1),
            monthlyFrequency=round(float(row['monthly_frequency']), 2),
            population=int(row['population']),
            pctOver60=round(float(row['pct_over60']), 1),
            estimatedTransactionVolume=round(float(row['transaction_volume']), 0),
            mttrGab=round(float(row['mttr_gab']), 1),
            incidentsWeekend=int(round(float(row['incidents_weekend']))),
            incidentsSemaine=int(round(float(row['incidents_semaine']))),
            ratioWeekend=round(float(row['ratio_weekend']), 3),
            jourPlusCritique=row['jour_plus_critique'],
            incidentsLundi=int(round(float(row['incidents_lundi']))),
            incidentsMardi=int(round(float(row['incidents_mardi']))),
            incidentsMercredi=int(round(float(row['incidents_mercredi']))),
            incidentsJeudi=int(round(float(row['incidents_jeudi']))),
            incidentsVendredi=int(round(float(row['incidents_vendredi']))),
            incidentsSamedi=int(round(float(row['incidents_samedi']))),
            incidentsDimanche=int(round(float(row['incidents_dimanche']))),
        )
        for row in rows
    ]


def get_at_risk_predictions() -> list[AtRiskPredictionItem]:
    rows = _latest_rows_for_atms()
    return [
        AtRiskPredictionItem(
            atmCode=row['atm'],
            agency=row['agency'],
            city=row['city'],
            typeGab=row['typeGab'] or 'Non renseigné',
            riskScore=row['riskScore'],
            failureProbability=row['failureProbability'],
            riskCategory=row['riskCategory'],
            dominantMotif=row['dominantMotif'],
            dominantCategory=row['dominantCategory'],
            mttrGab=round(float(row['mttr_gab']), 1),
            incidentsWeekend=int(round(float(row['incidents_weekend']))),
            incidentsSemaine=int(round(float(row['incidents_semaine']))),
            ratioWeekend=round(float(row['ratio_weekend']), 3),
            jourPlusCritique=row['jour_plus_critique'],
            explanation=_explanation(row),
            recommendation=_recommendation_for_features(row['riskCategory'], row),
        )
        for row in rows
    ]


def _latest_rows_for_atms() -> list[dict[str, Any]]:
    ensure_data_loaded()
    if not incidents:
        return []

    artifact = _get_failure_artifact()
    encoders = artifact.get('encoders', {}) if artifact else {'category': {}, 'motif': {}, 'type': {}, 'city': {}, 'agency': {}, 'critical_day': {}}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for incident in incidents:
        grouped[incident['atm']].append(incident)

    cutoff = max(item['reported_at'] for item in incidents)
    max_incidents_90d = max(
        sum(1 for incident in rows if cutoff - timedelta(days=90) <= incident['reported_at'] <= cutoff)
        for rows in grouped.values()
    )
    max_mttr = max(
        (sum(float(item.get('duration_min') or 0.0) for item in rows) / len(rows)) if rows else 0.0
        for rows in grouped.values()
    )
    rows: list[dict[str, Any]] = []

    for atm_serial, atm_incidents in grouped.items():
        feature_record = _build_feature_record(atm_serial, atm_incidents, cutoff, encoders)
        feature_values = [float(feature_record[column]) for column in FEATURE_COLUMNS]
        probability = _predict_probability_from_artifact(artifact, feature_values) if artifact else 0.0

        avg_duration = sum(item.get('duration_min', 0.0) for item in atm_incidents) / len(atm_incidents)
        distinct_categories = len({item.get('category', '') for item in atm_incidents})
        heuristic_score = (
            _safe_ratio(feature_record['incidents_90d'], max_incidents_90d) * 24
            + _safe_ratio(feature_record['mttr_gab'], max_mttr) * 18
            + min(feature_record['ratio_weekend'] / 0.35, 1) * 10
            + min(_max_weekday_incidents(feature_record) / 30, 1) * 7
            + min(distinct_categories / 4, 1) * 13
            + _category_weight(feature_record['dominantCategory']) * 0.12
            + probability * 16
        )
        risk_score = round(min(100, max(0, heuristic_score)), 1)
        rows.append({
            **feature_record,
            'riskScore': risk_score,
            'failureProbability': round(probability * 100, 1),
            'riskCategory': _risk_category(risk_score),
            'avgDuration': avg_duration,
            'incidentCount': len(atm_incidents),
            'distinctCategories': distinct_categories,
        })

    return sorted(rows, key=lambda item: (item['failureProbability'], item['riskScore']), reverse=True)


def _explanation(row: dict[str, Any]) -> str:
    reasons = []
    if row.get('incidents_90d', 0) >= 30:
        reasons.append('fréquence élevée sur les 90 derniers jours')
    if row.get('avgDuration', 0) >= 120:
        reasons.append('durée moyenne de résolution importante')
    if row.get('ratio_weekend', 0) >= 0.25:
        reasons.append('ratio weekend élevé')
    if row.get('jour_plus_critique') and row.get('jour_plus_critique') != 'Non renseigné':
        reasons.append(f"pic d’incidents le {row['jour_plus_critique']}")
    if row.get('distinctCategories', 0) >= 3:
        reasons.append('diversité des familles de pannes')
    if row.get('failureProbability', 0) >= 80:
        reasons.append('probabilité de panne élevée selon le modèle')
    if not reasons:
        reasons.append('historique incident modéré')
    return f"Ce GAB est {str(row.get('riskCategory', 'à surveiller')).lower()} en raison d’une " + ', '.join(reasons) + '.'


def get_top_critical_atms(limit: int = 5) -> List[TopCriticalATM]:
    rows = _latest_rows_for_atms()
    return [
        TopCriticalATM(
            atm=row['atm'],
            agency=row['agency'],
            city=row['city'],
            riskCategory=row['riskCategory'],
            riskScore=row['riskScore'],
            failureProbability=row['failureProbability'],
            topMotif=row['dominantMotif'],
            topCategory=row['dominantCategory'],
            averageDurationMinutes=round(row['avgDuration'], 1),
            incidentCount=row['incidentCount'],
            mttrGab=round(float(row['mttr_gab']), 1),
            incidentsWeekend=int(round(float(row['incidents_weekend']))),
            incidentsSemaine=int(round(float(row['incidents_semaine']))),
            ratioWeekend=round(float(row['ratio_weekend']), 3),
            jourPlusCritique=row['jour_plus_critique'],
            explanation=_explanation(row),
        )
        for row in rows[:limit]
    ]


def _actions_for_risk(row: dict[str, Any]) -> list[str]:
    actions = [
        f"Analyser le motif dominant: {row['dominantMotif']}",
        f"Contrôler la catégorie prioritaire: {row['dominantCategory']}",
    ]
    if row['riskCategory'] in {'Critique', 'Élevé'}:
        actions.insert(0, 'Planifier une intervention terrain prioritaire')
    else:
        actions.insert(0, 'Maintenir une surveillance renforcée')
    if row.get('mttr_gab', row.get('avgDuration', 0)) > 120:
        actions.append('Prioriser une analyse des délais d’intervention pour réduire le temps moyen de résolution.')
    if row.get('ratio_weekend', 0) >= 0.25:
        actions.append('Prévoir une surveillance renforcée pendant le weekend.')
    critical_day = row.get('jour_plus_critique')
    if critical_day and critical_day != 'Non renseigné':
        actions.append(f'Planifier une maintenance préventive avant le jour le plus critique: {critical_day}.')
    return actions


def get_recommendations(limit: int = 6) -> List[RecommendationItem]:
    rows = _latest_rows_for_atms()[:limit]
    priority_mapping = {
        'Critique': 'Urgente',
        'Élevé': 'Haute',
        'Moyen': 'Moyenne',
        'Faible': 'Standard',
    }

    return [
        RecommendationItem(
            atm=row['atm'],
            agency=row['agency'],
            city=row['city'],
            riskCategory=row['riskCategory'],
            priority=priority_mapping.get(row['riskCategory'], 'Standard'),
            actions=_actions_for_risk(row),
            topMotif=row['dominantMotif'],
            topCategory=row['dominantCategory'],
            recommendedAction=_recommendation_for_features(row['riskCategory'], row),
            businessJustification=(
                f"Planifier une intervention préventive car ce GAB présente {row['incidentCount']} incidents, "
                f"un MTTR de {round(float(row['mttr_gab']), 1)} min, "
                f"{int(round(float(row['incidents_weekend'])))} incidents weekend, "
                f"une catégorie dominante {row['dominantCategory']} et une probabilité de panne de {row['failureProbability']}%."
            ),
        )
        for row in rows
    ]
