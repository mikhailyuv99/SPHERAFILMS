"""Dedupe gallery, exclude founders/hero/brand assets from portfolio."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "site-data.json"

BRAND_IDS = {
    "a4671c3cdc93430705491cd465b7215a",
    "88c84b8adc504d0c6bc888ad132eb388",
    "4c51dd0398a1625f638af77912acc3e1",
    "84672a2709fae3b97a971eb98320ab9f",
    "c4fcce3364564e92d4ad555bf386937c",
    "9d7668e4c7c08e8cb1946a80bb5ede63",
    "15430ce4c716dcf666cc4d22e3a41eb4",
    "ed0daa89eb4c258242db825578b85c8e",
    "c9aa0e0d0679c4a111001079955af830",
    "94171031270bfe9aca961fa8679d9d51",
    "afea03826d98699578d72f995aecde38",
    "8d76b3aa5af47f3e9229754765cccf9e",
    "bdaa994ff318a0180e8f7347ec38ed93",
    "0bba10f772c36893da50ba66a1cae041",
    "9184fd18c8c2435d46d9dfd396824526",
    "65b841d9c6b2b61ae45be9881ae7db97",
    "9771207b0afeccc0e4f4cde7bd363366",
    "5c093d045eb7fcb08e378a1af2b355f8",
    "3cee74569b6270caff79a95787569469",
    "58173bf191ca69a669ca6a08606372a5",
    "fc2f20543a9918c2f89d5674dd1518b0",
    "0486027ee497aca970f2144ab2cd0eb0",
    "6fbf1b251541154a6934b7190875b5f4",
    "fd94faffd16c389f9343a0c4f1b6d660",
    "d925bcb22407bf9216272431883dd5d4",
    "a988a6c5bde226b78d47976c0be85b3a",
    "ece99664c5026f3bf74e9e58420344af",
    "132716e179c2035f3c1d642632355a92",
    "c75b4c094366f2f6d242d3cd027fb0d4",
    "95471e4a40b667fab94d711c30697a66",
    "b0470b57a414cddd102187a652fa360e",
    "fcdea0dbaaa87a98fd796f8f6908b316",
    "359a2a91c063a61ac4fb01a58347a01d",
    "58cdb9a2f7cce327825e711b67ead991",
    "536556aee892b7ba1f17321aa683cf2f",
    "e326174da2306cfbaa00b7bcde2a04ee",
    "fec4c46f59d2687154e3f364f3b1cff0",
    "fea1775c265beea9b248f4fa76d938d0",
}


def asset_id(path: str) -> str:
    return Path(path).stem


def is_brand(path: str) -> bool:
    return asset_id(path) in BRAND_IDS


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    exclude = {asset_id(p) for p in data.get("foundersPhotos", [])}
    exclude.add(asset_id(data.get("heroPoster", "")))

    gallery = []
    seen = set()
    for p in data.get("gallery", []):
        aid = asset_id(p)
        if aid in seen or aid in exclude or is_brand(p):
            continue
        if not (ROOT / p).is_file():
            continue
        seen.add(aid)
        gallery.append(p)

    data["gallery"] = gallery
    data["brandLogos"] = [
        f"assets/media/{aid}.png"
        for aid in BRAND_IDS
        if (ROOT / "assets" / "media" / f"{aid}.png").is_file()
    ]

    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"gallery: {len(gallery)} unique photos (excluded founders + hero poster + brands)")
    print(f"brandLogos: {len(data['brandLogos'])}")


if __name__ == "__main__":
    main()
