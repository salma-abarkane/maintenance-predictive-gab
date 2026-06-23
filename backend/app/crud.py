from collections import Counter
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from . import models
from .schemas import Summary, IncidentRecord, DemographicRecord, MapPoint, RiskPrediction, RecommendationItem
from .ml_model import RiskModel

CATEGORY_PRIORITY = {
    'Critique': 'Critique',
    'Élevé': 'Haute',
    'Moyen': 'Moyenne',
    'Faible': 'Standard'
}


def get_summary(db: Session) -> Summary:
    total_incidents = db.query(models.Incident).count()
    total_atms = db.query(models.ATM).count()
    total_agencies = db.query(models.Agency).count()
    total_cities = db.query(models.City).count()

    incident_trend = [
        {'month': 'Jan', 'incidents': 12},
        {'month': 'Fév', 'incidents': 18},
        {'month': 'Mar', 'incidents': 22},
        {'month': 'Avr', 'incidents': 27},
        {'month': 'Mai', 'incidents': 34},
        {'month': 'Juin', 'incidents': 39}
    ]

    return Summary(
        totalIncidents=total_incidents,
        totalAtms=total_atms,
        totalAgencies=total_agencies,
        totalCities=total_cities,
        incidentTrend=incident_trend
    )


def get_incidents(db: Session) -> List[IncidentRecord]:
    incidents = db.query(models.Incident).order_by(models.Incident.reported_at.desc()).all()
    return [
        IncidentRecord(
            id=incident.id,
            agency=db.query(models.Agency).filter(models.Agency.id == incident.agency_id).first().name,
            atm=db.query(models.ATM).filter(models.ATM.id == incident.atm_id).first().serial,
            city=incident.city,
            category=incident.category,
            severity=incident.severity,
            reportedAt=incident.reported_at.strftime('%Y-%m-%d %H:%M')
        )
        for incident in incidents
    ]


def get_demographics(db: Session) -> List[DemographicRecord]:
    cities = db.query(models.City).all()
    return [
        DemographicRecord(
            city=city.name,
            population=city.population,
            male=city.male,
            female=city.female,
            pctUnder15=city.pct_under15,
            pct15To59=city.pct_15_59,
            pctOver60=city.pct_over60
        )
        for city in cities
    ]


def get_map_points(db: Session) -> List[MapPoint]:
    city_counts = Counter()
    for incident in db.query(models.Incident).all():
        city_counts[incident.city] += 1

    points = []
    for agency in db.query(models.Agency).all():
        if agency.city in city_counts:
            points.append(MapPoint(city=agency.city, latitude=agency.latitude, longitude=agency.longitude, incidents=city_counts[agency.city]))

    unique_cities = {point.city: point for point in points}
    return list(unique_cities.values())


def get_predictions(db: Session, model: RiskModel) -> List[RiskPrediction]:
    atms = db.query(models.ATM).all()
    predictions = []
    for atm in atms:
        incident_count = db.query(models.Incident).filter(models.Incident.atm_id == atm.id).count()
        agency = db.query(models.Agency).filter(models.Agency.id == atm.agency_id).first()
        city = db.query(models.City).filter(models.City.name == agency.city).first()
        atm_age = max(1, 2024 - atm.year_installed)
        volume = 2000 + (incident_count * 200)
        preds = model.predict(
            incident_count=incident_count,
            atm_age=atm_age,
            population=city.population,
            pct_over60=city.pct_over60,
            transaction_volume=volume
        )
        predictions.append(RiskPrediction(atm=atm.serial, riskScore=preds['riskScore'], riskCategory=preds['riskCategory']))

    predictions.sort(key=lambda item: item.riskScore, reverse=True)
    return predictions


def get_recommendations(db: Session, model: RiskModel) -> List[RecommendationItem]:
    recommendations = []
    for prediction in get_predictions(db, model):
        priority = 'Basse'
        if prediction.riskCategory == 'Critique':
            priority = 'Immédiaire'
        elif prediction.riskCategory == 'Élevé':
            priority = 'Haute'
        elif prediction.riskCategory == 'Moyen':
            priority = 'Moyenne'

        agency = db.query(models.Agency).join(models.ATM).filter(models.ATM.serial == prediction.atm).first()
        actions = [
            'Vérifier l’alimentation électrique',
            'Prioriser l’intervention technique',
            'Planifier maintenance préventive dans la journée'
        ]
        recommendations.append(
            RecommendationItem(
                atm=prediction.atm,
                agency=agency.name,
                city=agency.city,
                riskCategory=prediction.riskCategory,
                priority=priority,
                actions=actions
            )
        )
    return recommendations


def get_prediction_from_request(model: RiskModel, incident_count: int, atm_age: int, population: int, pct_over60: float, transaction_volume: float):
    return model.predict(incident_count, atm_age, population, pct_over60, transaction_volume)
