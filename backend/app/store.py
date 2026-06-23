from datetime import datetime
from typing import Any, Dict, List, Optional

cities: List[Dict[str, Any]] = []
agencies: List[Dict[str, Any]] = []
atms: List[Dict[str, Any]] = []
incidents: List[Dict[str, Any]] = []


def reset_store() -> None:
    cities.clear()
    agencies.clear()
    atms.clear()
    incidents.clear()


def find_city(name: str) -> Optional[Dict[str, Any]]:
    return next((city for city in cities if city['name'].lower() == name.lower()), None)


def find_agency(name: str) -> Optional[Dict[str, Any]]:
    return next((agency for agency in agencies if agency['name'].lower() == name.lower()), None)


def find_atm(serial: str) -> Optional[Dict[str, Any]]:
    return next((atm for atm in atms if atm['serial'].lower() == serial.lower()), None)


def add_city(name: str, population: int, male: int, female: int, pct_under15: float, pct_15_59: float, pct_over60: float) -> Dict[str, Any]:
    existing = find_city(name)
    if existing:
        existing.update({
            'population': population,
            'male': male,
            'female': female,
            'pctUnder15': pct_under15,
            'pct15To59': pct_15_59,
            'pctOver60': pct_over60
        })
        return existing

    city = {
        'name': name,
        'population': population,
        'male': male,
        'female': female,
        'pctUnder15': pct_under15,
        'pct15To59': pct_15_59,
        'pctOver60': pct_over60
    }
    cities.append(city)
    return city


def add_agency(name: str, city: str, latitude: float, longitude: float) -> Dict[str, Any]:
    existing = find_agency(name)
    if existing:
        existing.update({'city': city or existing.get('city', ''), 'latitude': latitude, 'longitude': longitude})
        return existing

    agency = {'name': name, 'city': city, 'latitude': latitude, 'longitude': longitude}
    agencies.append(agency)
    return agency


def add_atm(serial: str, agency_name: str, location: str, year_installed: int = 2020) -> Dict[str, Any]:
    existing = find_atm(serial)
    if existing:
        existing.update({'agency': agency_name, 'location': location or existing.get('location', '')})
        return existing

    agency = find_agency(agency_name)
    atm = {
        'serial': serial,
        'agency': agency_name,
        'location': location,
        'year_installed': year_installed,
        'city': agency['city'] if agency else ''
    }
    atms.append(atm)
    return atm


def add_incident(
    agency: str,
    atm: str,
    city: str,
    category: str,
    severity: str,
    reported_at: datetime,
    duration_min: float = 0.0,
    motif: str = '',
    manager: str = '',
    state: str = '',
    source_month: str = ''
) -> Dict[str, Any]:
    incident = {
        'id': max((item['id'] for item in incidents), default=0) + 1,
        'agency': agency,
        'atm': atm,
        'city': city,
        'category': category,
        'severity': severity,
        'reported_at': reported_at,
        'duration_min': duration_min,
        'motif': motif,
        'manager': manager,
        'state': state,
        'source_month': source_month
    }
    incidents.append(incident)
    return incident


def incident_count_for_atm(serial: str) -> int:
    return sum(1 for incident in incidents if incident['atm'].lower() == serial.lower())


def incident_count_for_agency(name: str) -> int:
    return sum(1 for incident in incidents if incident['agency'].lower() == name.lower())


def incidents_by_city(city: str) -> List[Dict[str, Any]]:
    return [incident for incident in incidents if incident['city'].lower() == city.lower()]


def incident_cities() -> List[str]:
    return sorted({incident['city'] for incident in incidents})


def incidents_by_query(query: str) -> List[Dict[str, Any]]:
    query_lower = query.lower()
    return [incident for incident in incidents if query_lower in incident['agency'].lower() or query_lower in incident['atm'].lower()]
