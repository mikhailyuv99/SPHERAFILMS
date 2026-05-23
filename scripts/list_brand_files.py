"""Print brand PNG stems for manual mapping."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ids = [
    "a4671c3c", "84672a27", "c4fcce33", "9d7668e4", "ed0daa89",
    "c9aa0e0d", "94171031", "afea0382", "8d76b3aa", "bdaa994f",
    "0bba10f7", "0486027e", "58173bf1", "fc2f2054", "5c093d04",
    "3cee7456", "6fbf1b25", "fd94faff", "d925bcb2", "a988a6c5",
    "ece99664", "132716e1", "c75b4c09", "95471e4a", "b0470b57",
    "fcdea0db", "359a2a91", "58cdb9a2",
]
for i, stem in enumerate(ids, 1):
    matches = list((ROOT / "assets/media").glob(f"{stem}*"))
    if matches:
        print(i, matches[0].name, matches[0].stat().st_size)
