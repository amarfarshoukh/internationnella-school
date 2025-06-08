
import pandas as pd
import sqlite3
import os

csv_path = r"C:\student_data\student_dataset_with_exam_date.csv"  # Path to your CSV
db_path = "students.db"
chunksize = 100_000 

print(f"Estimating total number of lines in {csv_path} (this may take a while)...")
with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
    total_lines = sum(1 for _ in f)
total_rows = total_lines - 1  # exclude header
print(f"Estimated total rows (excluding header): {total_rows}")

print(f"Connecting to SQLite DB at {db_path}...")
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode = OFF;")
conn.execute("PRAGMA synchronous = OFF;")

rows_inserted = 0
chunk_num = 0
print("Starting CSV import in chunks...")
for chunk in pd.read_csv(csv_path, dtype=str, chunksize=chunksize):
    chunk.to_sql("students", conn, if_exists="append", index=False)
    rows_inserted += len(chunk)
    chunk_num += 1
    pct = (rows_inserted / total_rows) * 100
    print(f"Chunk {chunk_num}: Inserted {rows_inserted}/{total_rows} rows ({pct:.2f}%)")

print("All chunks inserted. Creating index for fast lookup...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_student_id ON students(CNTSTUID);")
conn.commit()
conn.close()
print("CSV successfully imported to SQLite and indexed!")