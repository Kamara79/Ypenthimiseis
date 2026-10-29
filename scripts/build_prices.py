"""Κρατάει από το ημερήσιο αρχείο τιμών (spyrosavl/posokanei) μόνο τα σούπερ μάρκετ της Σητείας."""
import json, sys, os, urllib.request, datetime

BASE = "https://raw.githubusercontent.com/spyrosavl/posokanei/main/data"

CHAINS = ["ab_vasilopoulos", "kritikos", "lidl", "halkiadakis"]

def aisles(snapshot):
    """Για κάθε κατηγορία, το όνομα της κατηγορίας 1ου επιπέδου (π.χ. «Καφές», «Γάλα»): περίπου ένας διάδρομος/ράφι."""
    cats = {c["category_id"]: c for c in snapshot["categories"]["categories"]}
    def top(cid):
        c = cats.get(cid)
        while c and c.get("depth", 0) > 1 and c.get("parent_id") in cats:
            c = cats[c["parent_id"]]
        return c["category_name"].replace("\u200b", "").strip() if c and c.get("depth", 0) == 1 else None
    return top


def regular_prices(snapshot, prev):
    """Για κάθε (προϊόν, αλυσίδα): η τελευταία τιμή που ΔΕΝ ήταν προσφορά.
    Παίρνει τις κανονικές τιμές από το χθεσινό prices.json· την πρώτη φορά ψάχνει έως 14 μέρες πίσω."""
    reg = {}
    for item in (prev or {}).get("products", []):
        for ch, v in item["p"].items():
            r = v[0] if not v[2] else (v[3] if len(v) > 3 else None)
            if r is not None:
                reg[(item["id"], ch)] = r
    if prev and any(len(v) > 3 for i in prev.get("products", []) for v in i["p"].values()):
        return reg
    day = datetime.date.fromisoformat(snapshot["date"])
    for back in range(14, 0, -1):
        d = day - datetime.timedelta(days=back)
        try:
            old = json.load(urllib.request.urlopen(f"{BASE}/{d.year}/posokanei-{d.isoformat()}.json", timeout=120))
        except Exception:
            continue
        for p in old["products"]:
            for r in p.get("retailer_prices") or []:
                if r.get("retailer") in CHAINS and r.get("country", "GR") == "GR" and r.get("price") is not None and not r.get("is_discount"):
                    reg[(p["id"], r["retailer"])] = r["price"]
    return reg


def build(snapshot, prev=None):
    top = aisles(snapshot)
    reg = regular_prices(snapshot, prev)
    out = []
    for p in snapshot["products"]:
        prices = {}
        for r in p.get("retailer_prices") or []:
            if r.get("retailer") in CHAINS and r.get("country", "GR") == "GR" and r.get("price") is not None:
                disc = bool(r.get("is_discount"))
                # 4ο στοιχείο: κανονική τιμή (χωρίς προσφορά), αν την ξέρουμε
                prices[r["retailer"]] = [r["price"], r.get("price_normalized"), disc,
                                         reg.get((p["id"], r["retailer"])) if disc else r["price"]]
        if not prices:
            continue
        item = {"id": p["id"], "n": p["name"].strip(), "u": p.get("unit"),
                "c": p.get("category"),
                "g": next((g for g in map(top, p.get("category_ids") or []) if g), p.get("subcategory")), "img": p.get("image_url") if p.get("has_image") else None,
                "p": prices}
        if p.get("price_drop"):
            item["drop"] = {k: p.get("price_drop_" + k) for k in ("company", "from", "to", "percentage", "end", "title")}
        out.append(item)
    return {"date": snapshot["date"], "chains": CHAINS, "products": out}

if __name__ == "__main__":
    snap = json.load(open(sys.argv[1], encoding="utf-8"))
    prev = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 and os.path.exists(sys.argv[3]) else None
    json.dump(build(snap, prev), open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
