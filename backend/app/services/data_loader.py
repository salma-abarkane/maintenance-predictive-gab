from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime
from threading import Lock
from pathlib import Path
from typing import Any

import pandas as pd

from ..store import add_agency, add_atm, add_city, add_incident, reset_store

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'

INCIDENTS_FILE = DATA_DIR / 'Pannes_GAB_Fusionnees(1) (1).xlsx'
RGPH_FILE = DATA_DIR / 'RGPH_2024_Banque_Populaire (1).xlsx'
MAPPING_FILE = DATA_DIR / 'Mapping_Agence_Ville.xlsx'
CITY_STATS_FILE = DATA_DIR / 'Statistiques_Villes.xlsx'

CITY_COORDS = {
    'rabat': (34.0209, -6.8417),
    'sale': (34.0333, -6.8000),
    'salé': (34.0333, -6.8000),
    'kenitra': (34.2610, -6.5802),
    'kénitra': (34.2610, -6.5802),
    'khemisset': (33.8240, -6.0663),
    'khémisset': (33.8240, -6.0663),
    'temara': (33.9287, -6.9067),
    'témara': (33.9287, -6.9067),
    'skhirat': (33.8522, -7.0317),
    'sidi kacem': (34.2215, -5.7078),
    'sidi slimane': (34.2648, -5.9256),
    'ouazzane': (34.7971, -5.5822),
    'ouezzane': (34.7971, -5.5822),
    'rommani': (33.5323, -6.6057),
    'tiflet': (33.8947, -6.3065),
}

_loaded = False
_load_lock = Lock()
_loaded_at: datetime | None = None
_last_error = ''


def _key(value: object) -> str:
    text = unicodedata.normalize('NFKD', str(value).strip().lower())
    text = ''.join(char for char in text if not unicodedata.combining(char))
    return re.sub(r'[^a-z0-9]+', '', text)


def _clean_str(value: object, fallback: str = '') -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return fallback
    text = str(value).strip()
    if text.lower() in {'nan', 'nat', 'none'}:
        return fallback
    return text


def _number(value: object, fallback: float = 0.0) -> float:
    if value is None or pd.isna(value):
        return fallback
    if isinstance(value, str):
        value = value.replace('%', '').replace(',', '.').strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _integer(value: object, fallback: int = 0) -> int:
    return int(round(_number(value, fallback)))


def _column(df: pd.DataFrame, aliases: list[str], required: bool = False) -> str | None:
    lookup = {_key(column): column for column in df.columns}
    for alias in aliases:
        found = lookup.get(_key(alias))
        if found is not None:
            return found
    if required:
        raise ValueError(f'Colonne manquante. Colonnes attendues: {", ".join(aliases)}')
    return None


def _cell(row: pd.Series, column: str | None, fallback: Any = '') -> Any:
    if column is None:
        return fallback
    value = row.get(column, fallback)
    return fallback if pd.isna(value) else value


def _read_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Fichier introuvable: {path}')
    return pd.read_excel(path, sheet_name=0)


def _city_coords(city: str) -> tuple[float, float]:
    normalized = _key(city)
    for name, coords in CITY_COORDS.items():
        if _key(name) in normalized or normalized in _key(name):
            return coords
    return (33.9716, -6.8498)


def _severity(category: str, duration_min: float) -> str:
    category_weight = {
        'hardware': 28,
        'reboot': 22,
        'software': 20,
        'communication': 20,
        'reseau': 20,
        'réseau': 20,
        'cash': 18,
    }
    score = min(duration_min / 6, 45)
    normalized_category = _key(category)
    score += next((weight for name, weight in category_weight.items() if _key(name) in normalized_category), 12)
    if score >= 55:
        return 'Critique'
    if score >= 35:
        return 'Élevé'
    if score >= 18:
        return 'Moyen'
    return 'Faible'


def _load_rgph() -> None:
    df = _read_excel(RGPH_FILE)
    city_col = _column(df, ['Zone', 'Ville', 'city'], required=True)
    population_col = _column(df, ['Population', 'population'])
    male_col = _column(df, ['Hommes', 'male', 'hommes'])
    female_col = _column(df, ['Femmes', 'female', 'femmes'])
    under15_col = _column(df, ['Moins_15_ans_%', 'pct_under15', 'Moins 15 ans'])
    age_15_59_col = _column(df, ['Age_15_59_ans_%', 'pct_15_59', '15-59 ans'])
    over60_col = _column(df, ['Plus_60_ans_%', 'pct_over60', 'Plus 60 ans'])

    for _, row in df.iterrows():
        city = _clean_str(_cell(row, city_col))
        if not city:
            continue
        add_city(
            city,
            population=_integer(_cell(row, population_col)),
            male=_integer(_cell(row, male_col)),
            female=_integer(_cell(row, female_col)),
            pct_under15=round(_number(_cell(row, under15_col)), 1),
            pct_15_59=round(_number(_cell(row, age_15_59_col)), 1),
            pct_over60=round(_number(_cell(row, over60_col)), 1),
        )


def _load_mapping() -> tuple[dict[str, str], dict[str, str]]:
    df = _read_excel(MAPPING_FILE)
    agency_col = _column(df, ['Agence', 'agency'], required=True)
    agency_code_col = _column(df, ['Code Agence', 'code_agence', 'CodeAgence'])
    city_col = _column(df, ['Ville', 'city', 'Zone'], required=True)

    agency_to_city: dict[str, str] = {}
    code_to_city: dict[str, str] = {}

    for _, row in df.iterrows():
        agency = _clean_str(_cell(row, agency_col))
        city = _clean_str(_cell(row, city_col))
        agency_code = _clean_str(_cell(row, agency_code_col))
        if not agency or not city:
            continue

        latitude, longitude = _city_coords(city)
        agency_entry = add_agency(agency, city, latitude, longitude)
        if agency_code:
            agency_entry['code'] = agency_code
            code_to_city[agency_code] = city
        agency_to_city[_key(agency)] = city

    return agency_to_city, code_to_city


def _load_city_stats() -> None:
    if not CITY_STATS_FILE.exists():
        return

    df = _read_excel(CITY_STATS_FILE)
    city_col = _column(df, ['Ville', 'city', 'Zone'])
    agencies_col = _column(df, ['Nombre_Agences', 'Nombre Agences'])
    atms_col = _column(df, ['Nombre_GAB', 'Nombre GAB'])
    if not city_col:
        return

    from ..store import find_city

    for _, row in df.iterrows():
        city_name = _clean_str(_cell(row, city_col))
        if not city_name:
            continue
        city = find_city(city_name)
        if city:
            city['agencyCount'] = _integer(_cell(row, agencies_col))
            city['atmCount'] = _integer(_cell(row, atms_col))


def _load_incidents(agency_to_city: dict[str, str], code_to_city: dict[str, str]) -> None:
    df = _read_excel(INCIDENTS_FILE)
    agency_col = _column(df, ['Agence'], required=True)
    agency_code_col = _column(df, ['Code Agence', 'CodeAgence'])
    atm_col = _column(df, ['Code GAB', 'CodeGAB', 'atm'])
    type_col = _column(df, ['Type GAB', 'TypeGAB'])
    reported_col = _column(df, ['Date & heure Réel', 'Date heure Reel', 'reported_at'], required=True)
    duration_col = _column(df, ['Durée (min)', 'Duree min', 'Duration'])
    category_col = _column(df, ['Catégorie', 'Categorie', 'category'])
    motif_col = _column(df, ['Motif', 'motif'])
    manager_col = _column(df, ['Gestionnaire', 'manager'])
    state_col = _column(df, ['Etat', 'État', 'state'])
    month_col = _column(df, ['Mois_Source', 'Mois Source'])

    for _, row in df.iterrows():
        agency = _clean_str(_cell(row, agency_col))
        agency_code = _clean_str(_cell(row, agency_code_col))
        atm = _clean_str(_cell(row, atm_col))
        if not atm and agency_code:
            atm = f'GAB-{agency_code}'
        category = _clean_str(_cell(row, category_col), 'Non classé')
        motif = _clean_str(_cell(row, motif_col), 'Non renseigné')
        duration = _number(_cell(row, duration_col))
        reported_at = pd.to_datetime(_cell(row, reported_col), errors='coerce')
        if not agency or not atm or pd.isna(reported_at):
            continue

        city = agency_to_city.get(_key(agency)) or code_to_city.get(agency_code) or 'Non mappée'
        latitude, longitude = _city_coords(city)
        add_agency(agency, city, latitude, longitude)
        atm_entry = add_atm(str(atm), agency, location=f'GAB {atm}', year_installed=2020)
        atm_entry['type'] = _clean_str(_cell(row, type_col))

        add_incident(
            agency=agency,
            atm=str(atm),
            city=city,
            category=category,
            severity=_severity(category, duration),
            reported_at=reported_at.to_pydatetime(),
            duration_min=duration,
            motif=motif,
            manager=_clean_str(_cell(row, manager_col)),
            state=_clean_str(_cell(row, state_col)),
            source_month=_clean_str(_cell(row, month_col)),
        )


def load_default_data(force: bool = False) -> None:
    global _loaded, _loaded_at, _last_error
    with _load_lock:
        if _loaded and not force:
            return

        try:
            reset_store()
            _load_rgph()
            agency_to_city, code_to_city = _load_mapping()
            _load_city_stats()
            _load_incidents(agency_to_city, code_to_city)
            _loaded = True
            _loaded_at = datetime.now()
            _last_error = ''
        except (FileNotFoundError, ValueError) as exc:
            _loaded = False
            _loaded_at = None
            _last_error = str(exc)
            raise


def ensure_data_loaded() -> None:
    load_default_data(force=False)


def get_data_status() -> dict[str, object]:
    from ..store import agencies, atms, cities, incidents

    return {
        'loaded': _loaded,
        'loadedAt': _loaded_at.isoformat(timespec='seconds') if _loaded_at else None,
        'lastError': _last_error,
        'files': {
            'incidents': INCIDENTS_FILE.exists(),
            'rgph': RGPH_FILE.exists(),
            'mapping': MAPPING_FILE.exists(),
            'cityStats': CITY_STATS_FILE.exists(),
        },
        'counts': {
            'incidents': len(incidents),
            'agencies': len(agencies),
            'atms': len(atms),
            'cities': len(cities),
        }
    }
