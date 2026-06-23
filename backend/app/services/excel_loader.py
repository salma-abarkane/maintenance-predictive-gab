import pandas as pd
from fastapi import UploadFile
from ..utils import excel_helpers
from ..store import add_agency, add_atm, add_city, add_incident, find_city, find_agency, find_atm


def _normalize_str(value: object) -> str:
    return str(value).strip()


def load_incidents_excel(upload_file: UploadFile) -> dict:
    workbook = excel_helpers.load_excel_file(upload_file, required_sheets=['Incidents'])
    incident_rows = pd.read_excel(workbook, sheet_name='Incidents')

    created_agencies = 0
    created_atms = 0
    updated_cities = 0
    imported_rows = 0

    for _, row in incident_rows.iterrows():
        city_name = _normalize_str(row.get('city', ''))
        agency_name = _normalize_str(row.get('agency', ''))
        atm_serial = _normalize_str(row.get('atm_serial', ''))
        category = _normalize_str(row.get('category', ''))
        severity = _normalize_str(row.get('severity', ''))
        reported_at = pd.to_datetime(row.get('reported_at'))

        if not city_name or not agency_name or not atm_serial:
            continue

        city = find_city(city_name)
        if city is None:
            add_city(city_name, population=0, male=0, female=0, pct_under15=0.0, pct_15_59=0.0, pct_over60=0.0)
            updated_cities += 1

        agency = find_agency(agency_name)
        if agency is None:
            add_agency(agency_name, city_name, latitude=0.0, longitude=0.0)
            created_agencies += 1

        atm = find_atm(atm_serial)
        if atm is None:
            add_atm(atm_serial, agency_name, location=atm_serial, year_installed=2020)
            created_atms += 1

        add_incident(
            agency=agency_name,
            atm=atm_serial,
            city=city_name,
            category=category,
            severity=severity,
            reported_at=reported_at
        )
        imported_rows += 1

    return {
        'message': 'Fichier incidents importé avec succès.',
        'importedRows': imported_rows,
        'createdAgencies': created_agencies,
        'createdAtms': created_atms,
        'updatedCities': updated_cities
    }


def load_rgph_excel(upload_file: UploadFile) -> dict:
    workbook = excel_helpers.load_excel_file(upload_file, required_sheets=['RGPH'])
    rgph_rows = pd.read_excel(workbook, sheet_name='RGPH')

    imported_rows = 0
    updated_cities = 0

    for _, row in rgph_rows.iterrows():
        city_name = _normalize_str(row.get('city', ''))
        if not city_name:
            continue

        population = int(row.get('population', 0))
        male = int(row.get('male', 0))
        female = int(row.get('female', 0))
        pct_under15 = float(row.get('pct_under15', 0.0))
        pct_15_59 = float(row.get('pct_15_59', 0.0))
        pct_over60 = float(row.get('pct_over60', 0.0))

        add_city(
            city_name,
            population=population,
            male=male,
            female=female,
            pct_under15=pct_under15,
            pct_15_59=pct_15_59,
            pct_over60=pct_over60
        )
        imported_rows += 1
        updated_cities += 1

    return {
        'message': 'Fichier RGPH importé avec succès.',
        'importedRows': imported_rows,
        'createdAgencies': 0,
        'createdAtms': 0,
        'updatedCities': updated_cities
    }
