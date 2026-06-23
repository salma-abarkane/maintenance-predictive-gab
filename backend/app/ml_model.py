class RiskModel:
    def __init__(self) -> None:
        self.model = None
        self.labels = ['Faible', 'Moyen', 'Élevé', 'Critique']

    def train(self) -> None:
        self.model = True

    def predict(self, incident_count: int, atm_age: int, population: int, pct_over60: float, transaction_volume: float):
        if self.model is None:
            raise ValueError('Le modèle n’a pas été entraîné.')

        score = incident_count * 3 + atm_age * 2 + (pct_over60 - 10) * 1.5 + (transaction_volume / 500)
        score = min(max(score, 0), 100)

        if score < 30:
            label_index = 0
        elif score < 55:
            label_index = 1
        elif score < 80:
            label_index = 2
        else:
            label_index = 3

        risk_score = float(round(score, 1))
        return {
            'riskScore': risk_score,
            'riskCategory': self.labels[label_index]
        }
