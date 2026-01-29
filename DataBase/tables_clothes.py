
"""
tables_clothes.py
-----------------
Creates 9 clothing tables (male/female/unisex × upper/lower/footwear) in ./fitme.db
with per-item PRICES stored directly in each table. Also SEEDS 100 items per gender
(≈34 upper, 33 lower, 33 footwear), each with a random BDT price.

Tables:
    male_upper_body,   male_lower_body,   male_footwear
    female_upper_body, female_lower_body, female_footwear
    unisex_upper_body, unisex_lower_body, unisex_footwear

Columns (all tables):
    id INTEGER PRIMARY KEY
    name TEXT NOT NULL
    size TEXT
    color TEXT
    material TEXT
    price_bdt INTEGER NOT NULL
    currency TEXT NOT NULL DEFAULT 'BDT'
    notes TEXT

Run:
    python tables_clothes.py
"""

from pathlib import Path
import sqlite3
import random

DB_PATH = Path("./fitme.db")  # edit if needed

TABLES = [
    "male_upper_body", "male_lower_body", "male_footwear",
    "female_upper_body", "female_lower_body", "female_footwear",
    "unisex_upper_body", "unisex_lower_body", "unisex_footwear",
]

def ensure_clothes_tables(cur):
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;
        -- Create if not exists with base columns; price columns may be added after via ALTER if missing
        CREATE TABLE IF NOT EXISTS male_upper_body (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS male_lower_body (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS male_footwear (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS female_upper_body (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS female_lower_body (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS female_footwear (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS unisex_upper_body (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS unisex_lower_body (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS unisex_footwear (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            size TEXT,
            color TEXT,
            material TEXT,
            price_bdt INTEGER,
            currency TEXT DEFAULT 'BDT',
            notes TEXT
        );
        """
    )
    # Ensure price columns exist (ADD if missing) and are NOT NULL by defaulting later during seed
    for t in TABLES:
        cols = {r[1] for r in cur.execute(f"PRAGMA table_info({t})").fetchall()}
        if "price_bdt" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN price_bdt INTEGER")
        if "currency" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN currency TEXT DEFAULT 'BDT'")

# ---------- Seeding helpers ----------
COLORS = [
    "Black","White","Navy","Beige","Olive","Grey","Charcoal","Teal","Maroon","Sky Blue",
    "Cream","Brown","Forest Green","Pastel Pink","Mustard","Khaki","Stone","Burgundy"
]
MATERIALS = ["Cotton","Linen","Polyester","Cotton-Blend","Wool","Denim","Leather","Canvas","Mesh","Silk-Blend","Chiffon"]
ADJ = ["Classic","Airy","Sport","Urban","Premium","Everyday","Smart","Relaxed","Heritage","Modern"]

UPPER_MALE = ["T-Shirt","Polo","Casual Shirt","Dress Shirt","Hoodie","Sweatshirt","Linen Shirt","Athletic Tee","Jersey","Kurta/Panjabi"]
LOWER_MALE = ["Jeans","Chinos","Trousers","Joggers","Shorts","Cargo Pants","Formal Trousers"]
FOOT_MALE  = ["Sneakers","Loafers","Derby Shoes","Sandals","Slides","Boots","Running Shoes"]

UPPER_FEMALE = ["Top","Blouse","Kurti","Cardigan","Tunic","Saree Blouse","Hoodie","Sweatshirt","Linen Shirt"]
LOWER_FEMALE = ["Jeans","Trousers","Palazzo","Leggings","Skirt","Chinos","Culottes"]
FOOT_FEMALE  = ["Sneakers","Flats","Sandals","Heels","Boots","Loafers"]

UPPER_UNI = ["T-Shirt","Hoodie","Sweatshirt","Jersey","Rain Jacket","Windbreaker","Polo"]
LOWER_UNI = ["Jeans","Joggers","Track Pants","Chinos","Shorts","Cargo Pants"]
FOOT_UNI  = ["Sneakers","Slides","Sandals","Running Shoes","Hiking Shoes","Loafers"]

def pick(seq):
    return random.choice(seq)

def round_to_50(x: int) -> int:
    return int(round(x / 50.0) * 50)

def price_for(table):
    # Category-based ranges
    if table.endswith("upper_body"):
        lo, hi = 400, 6000
    elif table.endswith("lower_body"):
        lo, hi = 500, 7000
    else:  # footwear
        lo, hi = 800, 12000
    return round_to_50(random.randint(lo, hi))

def size_for(table):
    if "upper_body" in table:
        if table.startswith("male"):
            return pick(["S","M","L","XL"])
        if table.startswith("female"):
            return pick(["XS","S","M","L","XL"])
        return pick(["XS","S","M","L","XL"])
    if "lower_body" in table:
        if table.startswith("male"):
            return str(pick([28,30,32,34,36,38,40]))
        if table.startswith("female"):
            return str(pick([26,27,28,29,30,31,32,34,36]))
        return pick(["XS","S","M","L","XL"])
    if "footwear" in table:
        if table.startswith("male"):
            return f"EU {pick([39,40,41,42,43,44,45,46])}"
        if table.startswith("female"):
            return f"EU {pick([36,37,38,39,40,41,42])}"
        return f"EU {pick([36,37,38,39,40,41,42,43,44,45,46])}"
    return "M"

def base_name(table):
    if table.startswith("male_"):
        if "upper_body" in table: base = pick(UPPER_MALE)
        elif "lower_body" in table: base = pick(LOWER_MALE)
        else: base = pick(FOOT_MALE)
    elif table.startswith("female_"):
        if "upper_body" in table: base = pick(UPPER_FEMALE)
        elif "lower_body" in table: base = pick(LOWER_FEMALE)
        else: base = pick(FOOT_FEMALE)
    else:
        if "upper_body" in table: base = pick(UPPER_UNI)
        elif "lower_body" in table: base = pick(LOWER_UNI)
        else: base = pick(FOOT_UNI)
    return base

def item_name(table):
    return f"{pick(ADJ)} {pick(COLORS)} {base_name(table)}"

def purge_all(cur):
    for t in TABLES:
        cur.execute(f"DELETE FROM {t}")

def seed_gender(cur, gender_prefix: str, total: int = 100):
    # 34/33/33 split
    u = 34
    l = 33
    f = 33
    targets = [
        (f"{gender_prefix}_upper_body", u),
        (f"{gender_prefix}_lower_body", l),
        (f"{gender_prefix}_footwear", f),
    ]
    for table, n in targets:
        rows = []
        seen = set()
        while len(rows) < n:
            name = item_name(table)
            if (name, table) in seen:
                continue
            seen.add((name, table))
            size = size_for(table)
            color = pick(COLORS)
            material = pick(MATERIALS)
            price = price_for(table)
            notes = "seeded"
            rows.append((name, size, color, material, price, "BDT", notes))
        cur.executemany(
            f"INSERT INTO {table}(name,size,color,material,price_bdt,currency,notes) VALUES (?,?,?,?,?,?,?)",
            rows
        )

def seed_all(cur, per_gender=100):
    purge_all(cur)
    seed_gender(cur, "male", per_gender)
    seed_gender(cur, "female", per_gender)
    seed_gender(cur, "unisex", per_gender)

def main():
    random.seed()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    ensure_clothes_tables(cur)
    seed_all(cur, per_gender=100)
    conn.commit()

    counts = {t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}
    print("✅ Seeded clothing tables (with prices)")
    for t in TABLES:
        lo = cur.execute(f"SELECT MIN(price_bdt) FROM {t}").fetchone()[0]
        hi = cur.execute(f"SELECT MAX(price_bdt) FROM {t}").fetchone()[0]
        print(f"  {t:20s} -> rows: {counts[t]:3d} | price min: {lo} | max: {hi}")

if __name__ == "__main__":
    main()
