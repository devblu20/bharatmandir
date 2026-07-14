"""
BharatMandir — Batch 1 Temple Inserter
Run this from your backend directory:

    cd bharatmandir/backend
    python run_batch1_insert.py

This script:
  1. Loads temples_batch1_10.csv from the data/ folder
  2. Validates all rows (expect: 11 valid, 0 invalid)
  3. Cleans each row
  4. Inserts into Neon PostgreSQL (skips duplicates via ON CONFLICT slug)
  5. Prints a full summary

Temples in this batch (11 total):
  1.  Omkareshwar Jyotirlinga Temple     — Khandwa, MP
  2.  Mamleshwar Temple                  — Omkareshwar, MP
  3.  Pashupatinath Temple Mandsaur      — Mandsaur, MP
  4.  Pitambara Peeth                    — Datia, MP
  5.  Shri Ram Raja Temple               — Orchha, MP
  6.  Chaturbhuj Temple Orchha           — Orchha, MP
  7.  Bijasan Mata Temple                — Indore, MP
  8.  Kanch Mandir Indore                — Indore, MP
  9.  Khajrana Ganesh Temple             — Indore, MP
  10. Annapurna Temple Indore            — Indore, MP
  11. Bawangaja Jain Temple              — Barwani, MP
"""

import sys
import os

# Make sure we can import from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.run_pipeline import run_pipeline

if __name__ == "__main__":
    # Path to the CSV (relative to backend/)
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "temples.csv"
    )

    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        print("   Place temples_batch1_10.csv inside bharatmandir/backend/data/")
        sys.exit(1)

    run_pipeline(csv_path)