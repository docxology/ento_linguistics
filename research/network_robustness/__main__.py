"""Execute the separately receipted full-abstract robustness extension."""

import sys
from pathlib import Path

from .study import Protocol, run

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "src"))
run(root, root / "output/extensions/network_robustness", Protocol())
