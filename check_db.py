# check_db.py
import sqlite3

conn = sqlite3.connect('o_fitme.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
    
    # Show first few rows if it's a clothing table
    if any(keyword in table[0] for keyword in ['male', 'female', 'unisex', 'upper', 'lower', 'footwear']):
        try:
            cursor.execute(f"SELECT * FROM {table[0]} LIMIT 2")
            rows = cursor.fetchall()
            print(f"    Sample data: {rows[:2]}")
        except:
            print(f"    Could not read data")

conn.close()