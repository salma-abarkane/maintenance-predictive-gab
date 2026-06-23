from typing import List
from ..schemas import RiskPrediction, RecommendationItem
from ..ml_model import RiskModel
from ..store import atms, agencies, cities, incidents


def build_risk_prediction(model: RiskModel) -> List[RiskPrediction]:
    predictions = []
    for atm in atms:
        incident_count = sum(1 for incident in incidents if incident['atm'] == atm['serial'])
        agency = next((agency for agency in agencies if agency['name'] == atm['agency']), None)
        city = next((city for city in cities if city['name'] == (agency['city'] if agency else '')), None)
        atm_age = max(1, 2024 - atm['year_installed'])
        transaction_volume = 2200 + (incident_count * 200)

        population = city['population'] if city else 300000
        pct_over60 = city['pctOver60'] if city else 12.0

        prediction = model.predict(
            incident_count=incident_count,
            atm_age=atm_age,
            population=population,
            pct_over60=pct_over60,
            transaction_volume=transaction_volume
        )

        predictions.append(
            RiskPrediction(
                atm=atm['serial'],
                riskScore=prediction['riskScore'],
                riskCategory=prediction['riskCategory']
            )
        )

    return sorted(predictions, key=lambda item: item.riskScore, reverse=True)


def build_recommendations(model: RiskModel) -> List[RecommendationItem]:
    recommendations = []
    predictions = build_risk_prediction(model)

    for prediction in predictions:
        atm = next((atm for atm in atms if atm['serial'] == prediction.atm), None)
        agency = next((agency for agency in agencies if agency and agency['name'] == (atm['agency'] if atm else '')), None)
        priority = {
            'Critique': 'Urgente',
            'Élevé': 'Haute',
            'Moyen': 'Moyenne',
            'Faible': 'Standard'
        }.get(prediction.riskCategory, 'Standard')

        actions = [
            'Planifier une visite de maintenance prioritaire',
            'Tester l’alimentation et les capteurs',
            'Mettre à jour la configuration logicielle du GAB'
        ]

        recommendations.append(
            RecommendationItem(
                atm=prediction.atm,
                agency=agency['name'] if agency else (atm['agency'] if atm else ''),
                city=agency['city'] if agency else (atm['city'] if atm else ''),
                riskCategory=prediction.riskCategory,
                priority=priority,
                actions=actions
            )
        )

    return recommendations
