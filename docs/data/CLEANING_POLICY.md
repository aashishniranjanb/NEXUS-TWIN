# Data Cleaning Policy & Preprocessing Documentation

| Metric | Value |
|---|---|
| **Raw Input** | `C:\Users\shang\OneDrive\Desktop\traffic AI\data\train.csv` |
| **Clean Output** | `C:\Users\shang\OneDrive\Desktop\traffic AI\data\processed\traffic_clean.parquet` |
| **Row Count** | 856,387 |
| **Column Count** | 31 |
| **Storage Size** | 16.21 MB (Parquet) |

---

## 1. Missing Value Policy

| Field | Missing Count | Policy Applied | Rationale |
|---|---|---|---|
| `EntryStreetName` | 8,148 (0.95%) | Imputed with `"UNKNOWN"` + created `entry_street_missing` binary flag (0/1) | Preserves row integrity while allowing models to capture any systematic missingness signal |
| `ExitStreetName` | 6,287 (0.73%) | Imputed with `"UNKNOWN"` + created `exit_street_missing` binary flag (0/1) | Preserves movement dynamics without dropping valuable intersection telemetry |

## 2. Integrity & Range Rules
- **Non-negative targets**: All 15 percentile behavioral metrics (`TotalTimeStopped_*`, `TimeFromFirstStop_*`, `DistanceToFirstStop_*`) verified >= 0.0.
- **Monotonicity**: Percentile order p20 <= p40 <= p50 <= p60 <= p80 verified with 0 violations across all rows.
- **Domain Constraints**: Hour in [0, 23], Weekend in {0, 1}, Month in [1, 12], City in {Atlanta, Boston, Chicago, Philadelphia}.

## 3. Storage Optimization
- Raw CSV (578 MB) is converted to compressed columnar Apache Parquet (16.21 MB).
- Downstream loading is >15x faster, eliminating repetitive CSV parsing overhead across training and EDA experiments.
