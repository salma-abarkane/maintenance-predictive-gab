from fastapi import APIRouter, HTTPException
from ..schemas import AtRiskPredictionItem, PredictionAtmFeatures, PredictionRequest, PredictionResponse, TopCriticalATM, RecommendationItem
from ..services import ai_service

router = APIRouter(prefix='/api/ai', tags=['ai'])
predict_router = APIRouter(prefix='/api', tags=['ai'])


@router.post('/train')
def train_model() -> dict:
    ai_service.train_model()
    return {'message': 'Modèle IA entraîné avec succès.'}


@router.post('/predict', response_model=PredictionResponse)
def predict_risk(request: PredictionRequest) -> PredictionResponse:
    try:
        prediction = ai_service.predict_failure_risk(request)
        return prediction
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@predict_router.post('/predict')
def predict_risk_short_route(request: PredictionRequest) -> dict:
    prediction = predict_risk(request)
    return {
        'code_gab': prediction.atmCode,
        'agence': prediction.agency,
        'ville': prediction.city,
        'risk_score': prediction.riskScore,
        'score_risque': prediction.riskScore,
        'risk_level': prediction.riskCategory,
        'niveau_risque': prediction.riskCategory,
        'probability': round(prediction.failureProbability / 100, 3),
        'probabilite_panne': round(prediction.failureProbability / 100, 3),
        'explanation': prediction.explanation,
        'mttr_gab': prediction.mttrGab,
        'incidents_weekend': prediction.incidentsWeekend,
        'incidents_semaine': prediction.incidentsSemaine,
        'ratio_weekend': prediction.ratioWeekend,
        'jour_plus_critique': prediction.jourPlusCritique,
        'motif_dominant': prediction.dominantMotif,
        'categorie_dominante': prediction.dominantCategory,
        'recommendation': prediction.recommendation,
        'recommandation': prediction.recommendation,
    }


@predict_router.get('/predict/atms', response_model=list[PredictionAtmFeatures])
def prediction_atms() -> list[PredictionAtmFeatures]:
    return ai_service.get_prediction_atms()


@predict_router.get('/predict/at-risk', response_model=list[AtRiskPredictionItem])
def at_risk_predictions() -> list[AtRiskPredictionItem]:
    return ai_service.get_at_risk_predictions()


@router.get('/top-critical', response_model=list[TopCriticalATM])
def top_critical_atms(limit: int = 5) -> list[TopCriticalATM]:
    return ai_service.get_top_critical_atms(limit=limit)


@router.get('/recommendations', response_model=list[RecommendationItem])
def get_recommendations(limit: int = 6) -> list[RecommendationItem]:
    return ai_service.get_recommendations(limit=limit)
