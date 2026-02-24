import sqlite3, json

conn = sqlite3.connect('gruha_alankara.db')
c = conn.cursor()

# List tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in c.fetchall()])

# Get latest design
for table in ['design', 'designs']:
    try:
        c.execute(f"SELECT id, image_path, room_type, style FROM {table} ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if row:
            print(f"\nLatest design from '{table}':")
            print(f"  ID: {row[0]}")
            print(f"  image_path raw: {row[1]}")
            print(f"  room_type: {row[2]}")
            print(f"  style: {row[3]}")
            try:
                paths = json.loads(row[1])
                print(f"  Parsed paths: {json.dumps(paths, indent=4)}")
            except:
                print(f"  (not JSON)")
    except Exception as e:
        print(f"  Table '{table}' error: {e}")

conn.close()
