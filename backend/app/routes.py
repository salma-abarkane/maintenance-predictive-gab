from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import (
    Summary,
    IncidentRecord,
    DemographicRecord,
    MapPoint,
    RiskPrediction,
    RecommendationItem,
    PredictionRequest,
    PredictionResponse,
    ExcelImportResponse
)
from .services import data_service, prediction_service, excel_loader
from .ml_model import RiskModel

router = APIRouter(prefix='/api', tags=['maintenance'])
model = RiskModel()


def get_model() -> RiskModel:
    if model.model is None:
        model.train()
    return model


@router.get('/summary', response_model=Summary)
def summary(db: Session = Depends(get_db)):
    return data_service.fetch_summary(db)


@router.get('/incidents', response_model=list[IncidentRecord])
def incidents(city: str | None = None, query: str | None = None, db: Session = Depends(get_db)):
    return data_service.list_incidents(db, city=city, query=query)


@router.get('/demographics', response_model=list[DemographicRecord])
def demographics(db: Session = Depends(get_db)):
    return data_service.list_demographics(db)


@router.get('/map', response_model=list[MapPoint])
def map_points(db: Session = Depends(get_db)):
    return data_service.list_map_points(db)


@router.get('/predictions', response_model=list[RiskPrediction])
def predictions(db: Session = Depends(get_db), model: RiskModel = Depends(get_model)):
    return prediction_service.build_risk_prediction(db, model)


@router.get('/recommendations', response_model=list[RecommendationItem])
def recommendations(db: Session = Depends(get_db), model: RiskModel = Depends(get_model)):
    return prediction_service.build_recommendations(db, model)


@router.post('/predict', response_model=PredictionResponse)
def predict(request: PredictionRequest, model: RiskModel = Depends(get_model)):
    prediction = model.predict(
        incident_count=request.incidentCount,
        atm_age=request.atmAge,
        population=request.population,
        pct_over60=request.pctOver60,
        transaction_volume=request.transactionVolume
    )
    return PredictionResponse(
        riskScore=prediction['riskScore'],
        riskCategory=prediction['riskCategory'],
        recommendation='Planifier une intervention prioritaire si le risque est Élevé ou Critique.'
    )


@router.post('/import/excel', response_model=ExcelImportResponse)
def import_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        result = excel_loader.load_excel_upload(file, db)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
