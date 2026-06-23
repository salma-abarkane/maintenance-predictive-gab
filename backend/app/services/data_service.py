from collections import Counter
from typing import List
from ..schemas import Summary, IncidentRecord, DemographicRecord, MapPoint
from ..store import agencies, cities, incidents, atms
from .data_loader import ensure_data_loaded


def fetch_summary() -> Summary:
    ensure_data_loaded()
    total_incidents = len(incidents)
    total_atms = len(atms)
    total_agencies = len({agency['name'] for agency in agencies})
    total_cities = len(cities)
    from .incident_service import get_monthly_incidents

    incident_trend = [
        {'month': item.month, 'incidents': item.incidentCount}
        for item in get_monthly_incidents()
    ]

    return Summary(
        totalIncidents=total_incidents,
        totalAtms=total_atms,
        totalAgencies=total_agencies,
        totalCities=total_cities,
        incidentTrend=incident_trend
    )


def list_incidents(city: str | None = None, query: str | None = None) -> List[IncidentRecord]:
    ensure_data_loaded()
    filtered_incidents = incidents
    if city and city.lower() != 'toutes':
        filtered_incidents = [item for item in filtered_incidents if item['city'].lower() == city.lower()]

    if query:
        q = query.lower()
        filtered_incidents = [
            item for item in filtered_incidents
            if q in item['agency'].lower() or q in item['atm'].lower()
        ]

    sorted_incidents = sorted(filtered_incidents, key=lambda item: item['reported_at'], reverse=True)
    return [
        IncidentRecord(
            id=item['id'],
            agency=item['agency'],
            atm=item['atm'],
            city=item['city'],
            category=item['category'],
            severity=item['severity'],
            reportedAt=item['reported_at'].strftime('%Y-%m-%d %H:%M')
        )
        for item in sorted_incidents
    ]


def list_demographics() -> List[DemographicRecord]:
    ensure_data_loaded()
    sorted_cities = sorted(cities, key=lambda city: city['name'])
    return [
        DemographicRecord(
            city=city['name'],
            population=city['population'],
            male=city['male'],
            female=city['female'],
            pctUnder15=city['pctUnder15'],
            pct15To59=city['pct15To59'],
            pctOver60=city['pctOver60']
        )
        for city in sorted_cities
    ]


def list_map_points() -> List[MapPoint]:
    ensure_data_loaded()
    city_counts = Counter(item['city'] for item in incidents)
    gab_counts = Counter(atm.get('city') or next((incident['city'] for incident in incidents if incident['atm'] == atm['serial']), '') for atm in atms)
    try:
        from .ai_service import get_top_critical_atms
        risk_rows = get_top_critical_atms(limit=1000)
    except Exception:
        risk_rows = []
    risk_by_city: dict[str, list[float]] = {}
    for row in risk_rows:
        risk_by_city.setdefault(row.city, []).append(row.riskScore)

    def risk_category(score: float) -> str:
        if score >= 75:
            return 'Critique'
        if score >= 55:
            return 'Élevé'
        if score >= 30:
            return 'Moyen'
        return 'Faible'

    points: List[MapPoint] = []
    sorted_agencies = sorted(agencies, key=lambda agency: agency['city'])
    for agency in sorted_agencies:
        if agency['city'] in city_counts:
            city_risks = risk_by_city.get(agency['city'], [])
            average_risk = round(sum(city_risks) / len(city_risks), 1) if city_risks else 0.0
            points.append(
                MapPoint(
                    city=agency['city'],
                    latitude=agency['latitude'],
                    longitude=agency['longitude'],
                    incidents=city_counts[agency['city']],
                    gabCount=gab_counts.get(agency['city'], 0),
                    averageRiskScore=average_risk,
                    riskCategory=risk_category(average_risk)
                )
            )

    unique_cities = {point.city: point for point in points}
    return list(unique_cities.values())
