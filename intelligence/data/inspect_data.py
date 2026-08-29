import pandas as pd
from pathlib import Path

# Resolve path relative to project root or current directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "train.csv"

if not DATA_PATH.exists():
    DATA_PATH = Path("data/train.csv")

print("Loading dataset...")
print(f"Reading from: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

print("\n========== DATASET SHAPE ==========")
print(df.shape)

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== COLUMNS ==========")
for column in df.columns:
    print(column)

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== BASIC STATISTICS ==========")
print(df.describe(include="all"))
