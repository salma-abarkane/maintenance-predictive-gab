from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))

from backend.app.services.ai_service import _build_training_dataset
from backend.app.services.data_loader import load_default_data


def main() -> None:
    load_default_data(force=True)
    rows, targets, _, threshold = _build_training_dataset()
    positives = sum(targets)
    print(f'Lignes ML: {len(rows)}')
    print(f'Cibles positives: {positives}')
    print(f'Cibles négatives: {len(targets) - positives}')
    print(f'Seuil critique moyen du mois suivant: {threshold}')


if __name__ == '__main__':
    main()
