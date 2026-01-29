
"""
tables_prices.py
----------------
No separate price tables. This script *updates* per-item prices stored inside each of the 9
clothing tables created by tables_clothes.py. It also drops any legacy tables named 'prices_*'.

Run:
    python tables_prices.py
"""

from pathlib import Path
import sqlite3
import random

DB_PATH = Path("./fitme.db")

CLOTHING_TABLES = [
    "male_upper_body", "male_lower_body", "male_footwear",
    "female_upper_body", "female_lower_body", "female_footwear",
    "unisex_upper_body", "unisex_lower_body", "unisex_footwear",
]

def drop_legacy_price_tables(cur):
    rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'prices_%'").fetchall();
    for (name,) in rows:
        cur.execute(f"DROP TABLE IF EXISTS {name}")

def ensure_price_columns(cur):
    for t in CLOTHING_TABLES:
        cols = {r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()}
        if "price_bdt" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN price_bdt INTEGER")
        if "currency" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN currency TEXT DEFAULT 'BDT'")

def round_to_50(x: int) -> int:
    return int(round(x / 50.0) * 50)

def price_for(table):
    if table.endswith("upper_body"):
        lo, hi = 400, 6000
    elif table.endswith("lower_body"):
        lo, hi = 500, 7000
    else:
        lo, hi = 800, 12000
    return round_to_50(random.randint(lo, hi))

def refresh_prices(cur):
    for t in CLOTHING_TABLES:
        ids = [r[0] for r in cur.execute(f"SELECT id FROM {t}").fetchall()]
        for iid in ids:
            cur.execute(f"UPDATE {t} SET price_bdt=?, currency='BDT' WHERE id=?", (price_for(t), iid))

def main():
    random.seed()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # ensure clothing tables exist
    existing = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    missing = [t for t in CLOTHING_TABLES if t not in existing]
    if missing:
        raise RuntimeError(f"Missing clothing tables: {missing}. Run tables_clothes.py first.")

    drop_legacy_price_tables(cur)
    ensure_price_columns(cur)
    refresh_prices(cur)
    conn.commit()

    for t in CLOTHING_TABLES:
        cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        lo  = cur.execute(f"SELECT MIN(price_bdt) FROM {t}").fetchone()[0]
        hi  = cur.execute(f"SELECT MAX(price_bdt) FROM {t}").fetchone()[0]
        print(f" {t:20s} -> rows: {cnt:3d} | min: {lo} | max: {hi}")

if __name__ == "__main__":
    main()
