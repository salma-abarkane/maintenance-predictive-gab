from datetime import datetime
from sqlalchemy.orm import Session
from . import models

CITY_DATA = [
    {'name': 'Rabat', 'population': 1540000, 'male': 740000, 'female': 800000, 'pct_under15': 24.1, 'pct_15_59': 62.7, 'pct_over60': 13.2},
    {'name': 'Salé', 'population': 1430000, 'male': 700000, 'female': 730000, 'pct_under15': 25.5, 'pct_15_59': 61.8, 'pct_over60': 12.7},
    {'name': 'Salé Al Jadida', 'population': 430000, 'male': 210000, 'female': 220000, 'pct_under15': 26.4, 'pct_15_59': 60.9, 'pct_over60': 12.7},
    {'name': 'Skhirat-Témara', 'population': 640000, 'male': 310000, 'female': 330000, 'pct_under15': 23.6, 'pct_15_59': 63.5, 'pct_over60': 12.9},
    {'name': 'Kénitra', 'population': 981000, 'male': 478000, 'female': 503000, 'pct_under15': 24.8, 'pct_15_59': 62.1, 'pct_over60': 13.1},
    {'name': 'Sidi Kacem', 'population': 275000, 'male': 136000, 'female': 139000, 'pct_under15': 27.0, 'pct_15_59': 59.4, 'pct_over60': 13.6},
    {'name': 'Sidi Slimane', 'population': 330000, 'male': 163000, 'female': 167000, 'pct_under15': 27.8, 'pct_15_59': 58.9, 'pct_over60': 13.3},
    {'name': 'Khémisset', 'population': 250000, 'male': 123000, 'female': 127000, 'pct_under15': 25.9, 'pct_15_59': 60.5, 'pct_over60': 13.6},
    {'name': 'Ouazzane', 'population': 210000, 'male': 104000, 'female': 106000, 'pct_under15': 28.1, 'pct_15_59': 57.8, 'pct_over60': 14.1}
]

AGENCY_DATA = [
    {'name': 'Agence Rabat-Ville', 'city': 'Rabat', 'latitude': 34.0209, 'longitude': -6.8417},
    {'name': 'Agence Hassan', 'city': 'Rabat', 'latitude': 34.0216, 'longitude': -6.8299},
    {'name': 'Agence Salé Centre', 'city': 'Salé', 'latitude': 34.0249, 'longitude': -6.8198},
    {'name': 'Agence Skhirat', 'city': 'Skhirat-Témara', 'latitude': 33.8882, 'longitude': -6.9056},
    {'name': 'Agence Kénitra Nord', 'city': 'Kénitra', 'latitude': 34.2564, 'longitude': -6.5860},
    {'name': 'Agence Sidi Kacem', 'city': 'Sidi Kacem', 'latitude': 34.2545, 'longitude': -5.8760},
    {'name': 'Agence Sidi Slimane', 'city': 'Sidi Slimane', 'latitude': 34.2525, 'longitude': -5.8866},
    {'name': 'Agence Khémisset', 'city': 'Khémisset', 'latitude': 33.8114, 'longitude': -6.0655},
    {'name': 'Agence Ouazzane', 'city': 'Ouazzane', 'latitude': 35.2667, 'longitude': -5.5667}
]

INCIDENTS = [
    {'agency': 'Agence Rabat-Ville', 'atm': 'GAB Rabat 01', 'city': 'Rabat', 'category': 'Alimentation', 'severity': 'Élevé', 'reported_at': datetime(2024, 5, 18, 9, 30)},
    {'agency': 'Agence Rabat-Ville', 'atm': 'GAB Rabat 02', 'city': 'Rabat', 'category': 'Papier', 'severity': 'Moyen', 'reported_at': datetime(2024, 5, 21, 14, 55)},
    {'agency': 'Agence Hassan', 'atm': 'GAB Hassan 01', 'city': 'Rabat', 'category': 'Connectivité', 'severity': 'Critique', 'reported_at': datetime(2024, 5, 23, 11, 20)},
    {'agency': 'Agence Salé Centre', 'atm': 'GAB Salé 01', 'city': 'Salé', 'category': 'Alimentation', 'severity': 'Élevé', 'reported_at': datetime(2024, 6, 2, 8, 10)},
    {'agency': 'Agence Kénitra Nord', 'atm': 'GAB Kénitra 01', 'city': 'Kénitra', 'category': 'Capteur', 'severity': 'Critique', 'reported_at': datetime(2024, 6, 5, 13, 45)},
    {'agency': 'Agence Skhirat', 'atm': 'GAB Témara 01', 'city': 'Skhirat-Témara', 'category': 'Maintenance', 'severity': 'Moyen', 'reported_at': datetime(2024, 6, 7, 10, 30)},
    {'agency': 'Agence Sidi Kacem', 'atm': 'GAB Sidi Kacem 01', 'city': 'Sidi Kacem', 'category': 'Papier', 'severity': 'Faible', 'reported_at': datetime(2024, 6, 8, 16, 12)},
    {'agency': 'Agence Khémisset', 'atm': 'GAB Khémisset 01', 'city': 'Khémisset', 'category': 'Alimentation', 'severity': 'Élevé', 'reported_at': datetime(2024, 6, 9, 9, 5)},
    {'agency': 'Agence Ouazzane', 'atm': 'GAB Ouazzane 01', 'city': 'Ouazzane', 'category': 'Connectivité', 'severity': 'Critique', 'reported_at': datetime(2024, 6, 10, 12, 40)}
]


def seed_data(db: Session):
    existing = db.query(models.City).first()
    if existing:
        return

    for city in CITY_DATA:
        db.add(models.City(**city))
    db.commit()

    agencies = []
    for agency in AGENCY_DATA:
        obj = models.Agency(**agency)
        db.add(obj)
        agencies.append(obj)
    db.commit()

    for idx, agency in enumerate(agencies, start=1):
        for atm_index in range(1, 4):
            db.add(models.ATM(serial=f'ATM-{agency.name.replace(" ", "-")}-{atm_index}', agency_id=agency.id, location=f'{agency.name} - Terminal {atm_index}', year_installed=2018 + (atm_index % 5)))
    db.commit()

    for incident in INCIDENTS:
        atm = db.query(models.ATM).filter(models.ATM.serial.startswith(f"ATM-{incident['agency'].replace(' ', '-')}")).first()
        agency = db.query(models.Agency).filter(models.Agency.name == incident['agency']).first()
        if atm and agency:
            db.add(models.Incident(atm_id=atm.id, agency_id=agency.id, city=incident['city'], category=incident['category'], severity=incident['severity'], reported_at=incident['reported_at']))
    db.commit()
