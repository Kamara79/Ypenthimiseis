"""Κρατάει από το ημερήσιο αρχείο τιμών (spyrosavl/posokanei) μόνο τα σούπερ μάρκετ της Σητείας."""
import json, sys

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


def build(snapshot):
    top = aisles(snapshot)
    out = []
    for p in snapshot["products"]:
        prices = {}
        for r in p.get("retailer_prices") or []:
            if r.get("retailer") in CHAINS and r.get("country", "GR") == "GR" and r.get("price") is not None:
                prices[r["retailer"]] = [r["price"], r.get("price_normalized"), bool(r.get("is_discount"))]
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
    json.dump(build(snap), open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
