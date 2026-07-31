## Project Overview

The pipeline automatically collects Air Quality Index (AQI) data every 15 minutes for five cities, processes the collected data through an ETL workflow, stores it in a PostgreSQL data warehouse, and makes it available for visualization.

---

# Architecture Diagram

```text
              Air Quality API
                     │
                     ▼
          GitHub Actions (every 15 minutes)
                     │
                     ▼
                 Data Collection
                     │
                     ▼
                  raw/ Storage
                     │
                     ▼
              Data Transformation
                     │
                     ▼
              clean/final.csv
                     │
                     ▼
             load_warehouse.py
                     │
                     ▼
         PostgreSQL Data Warehouse (Neon)
                     │
                     ▼
              Power BI Dashboard
```

---

## Technology Stack

| Component | Tool | Justification |
|-----------|------|---------------|
| Programming Language | Python | Main language used to implement the ETL pipeline |
| AQI API | OpenWeather API | Provides hourly air quality data |
| HTTP Client | Requests | Retrieves data from the API |
| Data Processing | Pandas | Cleans and transforms raw data |
| Orchestrator | GitHub Actions | Automates hourly execution |
| Storage | raw/ & clean/ | Separates immutable raw data from processed data |
| Data Warehouse | PostgreSQL | Stores dimensional analytical data |
| Visualization | Power BI | Creates dashboards for AQI analysis |
| Version Control | Git & GitHub | Collaboration and source code management |

---

## ETL Workflow

### 1. Extract

- Collect hourly AQI data from the API.
- Retrieve historical data through a replayable backfill script.
- Store every API response in `raw/`.

### 2. Transform

- Read every file in `raw/`.
- Remove duplicates.
- Standardize data types and units.
- Sort observations chronologically.
- Generate a single `clean/final.csv`.

### 3. Load

- Read `clean/final.csv`.
- Populate the PostgreSQL warehouse.
- Update fact and dimension tables.

---

## Storage Strategy

### raw/

- Original API responses.
- Never modified.
- Serves as the project's backup.

### clean/

- Rebuilt at every execution.
- Contains the consolidated dataset (`clean/final.csv`), rebuilt at every execution.
- Used as the source for warehouse loading.

---

## Data Warehouse Design

### Schema

| Choice | Reason |
|--------|--------|
| **Star Schema** | Chosen for its simplicity, efficient querying, and suitability for data analysis. |

### Fact Table

- `fact_air_quality`

Measures include:
- AQI
- PM2.5
- PM10
- NO₂
- O₃
- Other available pollutants

### Dimension Tables

**dim_city**
- City
- Country
- Latitude
- Longitude

**dim_time**
- Date
- Hour
- Day of week
- Weekend indicator

---

## Automation

The pipeline is scheduled to run automatically every 15 minutes using GitHub Actions. Each execution performs the complete ETL process, ensuring that both the clean dataset and the data warehouse remain up to date.

---

## Design Choices

| Choice | Reason |
|--------|--------|
| GitHub Actions | Free and reliable scheduled workflow automation |
| Python | Simple and efficient for ETL development |
| PostgreSQL | Well suited for dimensional data warehousing |
| Power BI | Provides interactive dashboards for analytics |
| Star Schema | Optimized for reporting and analytical queries |
