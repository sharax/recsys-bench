"""Config for Recsys bench, mutable under certain conditions"""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"


@dataclass(frozen=True)
class Dataset:
    name: str
    ratings_path: Path
    separator: str
    has_header: bool
    expected_raw_rows: int


ML1M = Dataset(
    name="ml-1m",
    ratings_path=RAW / "ml-1m" / "ratings.dat",
    separator="::",
    has_header=False,
    expected_raw_rows=1_000_209,
)

ML32M = Dataset(
    name="ml-32m",
    ratings_path=RAW / "ml-32m" / "ratings.csv",
    separator=",",
    has_header=True,
    expected_raw_rows=32_000_204,
)

DATASETS = {d.name: d for d in (ML1M, ML32M)}

# --- protocol decisions, documented in the README ---

# MovieLens is explicit feedback (1-5 stars); we model implicit retrieval.
# 4.0 is the standard threshold and matches the Rendle et al. setup.
POSITIVE_THRESHOLD = 4.0

# Users below this are dropped before splitting: leave-last-out needs at
# least 3 train interactions after removing val and test.
MIN_INTERACTIONS = 5

TOP_K = 20
N_BOOTSTRAP = 1000
SEED = 20261014
