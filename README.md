# PROJECT DONNEES 2 - DataPulse

## Description

An automated ETL pipeline that collects air quality data every 15 minutes from public APIs, transforms it into a clean and standardized dataset, stores it in a dimensional data warehouse, and provides dashboards for air quality analysis.

---

## Team Members

| Team Member | Role | Responsibilities |
|-------------|------|------------------|
| Tokiniaina | Data Engineer – Collection | Collect AQI data, manage API, implement backfill |
| Eric | Data Engineer – Orchestration | Automate ETL, schedule jobs, deploy pipeline |
| Rado | Data Engineer – Transformation | Clean, validate, and transform data |
| Toavina | Data Modeler | Design warehouse schema and load data |
| Sitraka | Lead Documentation & QA | Documentation, project coordination, quality assurance |

---

## Cities Covered

| City | Country | Latitude | Longitude |
|------|---------|----------|-----------|
| Antananarivo | Madagascar | -18.8792 | 47.5079 |
| London | United Kingdom | 51.5074 | -0.1278 |
| Moscow | Russia | 55.7558 | 37.6173 |
| Paris | France | 48.8566 | 2.3522 |
| Washington, D.C. | United States | 38.9072 | -77.0369 |

---

## Data Contract (`clean/final.csv`)

| Column | Type | Unit | Description |
|---------|------|------|-------------|
| city | String | — | City name |
| country | String | — | Country name |
| latitude | Float | Degrees | Latitude |
| longitude | Float | Degrees | Longitude |
| timestamp | Datetime | UTC | Observation date and time |
| aqi | Integer | AQI | Air Quality Index |
| pm2_5 | Float | µg/m³ | PM2.5 concentration |
| pm10 | Float | µg/m³ | PM10 concentration |
| no2 | Float | µg/m³ | Nitrogen dioxide concentration |
| o3 | Float | µg/m³ | Ozone concentration |
| ... | ... | ... | Additional pollutants depending on the API |

---

## Data Coverage

- **Cities:** 5
- **Collection frequency:** Every 15 minutes
- **Backfill period:** 4 months of historical data
- **Timezone:** UTC

---

## Data Warehouse


### Dimensions
- `dim_city`
- `dim_time`

### Fact Table
- `fact_air_quality`

---

## Known Limitations

- Missing observations may occur because of API downtime.
- API rate limits may delay some collections.
- Missing values are documented whenever applicable.

---

## Database Connection

| Item | Value |
|------|-------|
| Database | PostgreSQL (Neon) |
| Host | ep-red-brook-axxipcj4-pooler.c-4.us-east-2.aws.neon.tech |
| Port | 5432 |
| Database Name | neondb |

> Authentication credentials are not included in this repository.

---

## Repository Structure

```text
raw/
clean/
warehouse/
scripts/
ARCHITECTURE.md
README.md
requirements.txt
```


