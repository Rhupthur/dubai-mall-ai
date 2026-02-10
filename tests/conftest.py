import sys
from pathlib import Path

# Ajoute la racine du projet au sys.path pour que:
# import data_layer / logic_layer / routers_layer / main fonctionne
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
