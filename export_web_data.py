"""Export results/*.csv to web/public/data.json for the React dashboard."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
NAMES = ["second_price", "second_price_bids", "fixed_bids", "first_price", "vcg_payments", "vcg_deviations"]


def main(src=ROOT / "results", dst=ROOT / "web" / "public" / "data.json"):
    data = {}
    for name in NAMES:
        df = pd.read_csv(Path(src) / f"{name}.csv", dtype={"value": str} if name == "first_price" else None)
        df = df.round(6).astype(object).where(df.notna(), None)
        data[name] = df.to_dict("records")
    meta = json.loads((Path(src) / "validation.json").read_text(encoding="utf-8"))
    data["meta"] = {"trials": meta.get("trials"), "seed": meta.get("seed")}
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print("wrote", dst)


if __name__ == "__main__":
    main()
