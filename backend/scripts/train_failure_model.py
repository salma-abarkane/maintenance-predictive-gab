from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from backend.app.services.ai_service import get_model_metrics, train_model
from backend.app.services.data_loader import load_default_data


def main() -> None:
    load_default_data(force=True)
    train_model()
    metrics = get_model_metrics()
    print('Modèle entraîné.')
    for name, value in metrics.items():
        print(f'{name}: {value}')


if __name__ == '__main__':
    main()
