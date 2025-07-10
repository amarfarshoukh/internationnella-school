import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load only the needed columns to minimize memory usage
csv_file = r"C:\Users\user\OneDrive - Lebanese University\Desktop\adaptive-learning-system\Database\student_dataset.csv"
chunksize = 100_000  # Adjust based on your RAM

# Function to generate random exam dates
def generate_random_dates(start_date, end_date, n):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [start + timedelta(days=np.random.randint(0, (end - start).days)) for _ in range(n)]

# First pass: get total number of rows
print("Counting rows...")
row_count = sum(1 for _ in open(csv_file)) - 1  # subtract header
print(f"Total rows: {row_count}")

# Generate random exam dates
exam_dates = generate_random_dates("2025-06-10", "2025-07-10", row_count) ##THIS

# Second pass: load and append ExamDate
print("Processing in chunks and saving new file...")
reader = pd.read_csv(csv_file, chunksize=chunksize)

output_file = r"C:\Users\user\OneDrive - Lebanese University\Desktop\adaptive-learning-system\Database\student_dataset_with_exam_date_presentation.csv"

with open(output_file, "w", encoding="utf-8", newline='') as f_out:
    for i, chunk in enumerate(reader):
        start = i * chunksize
        end = start + len(chunk)
        chunk["ExamDate"] = exam_dates[start:end]
        # Write header only for the first chunk
        chunk.to_csv(f_out, index=False, header=(i == 0))

print(" Done! File saved as 'student_dataset_with_exam_date_presentation.csv' ")