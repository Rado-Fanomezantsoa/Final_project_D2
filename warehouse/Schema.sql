-- -----------------------------------------------------------------------------
-- DIM_CITY : une ligne par ville suivie (référentiel statique, 5 lignes)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_city (
    city_id     SERIAL PRIMARY KEY,
    city        VARCHAR(100) NOT NULL,
    country     VARCHAR(100) NOT NULL,
    latitude    NUMERIC(9,6) NOT NULL,
    longitude   NUMERIC(9,6) NOT NULL,
    UNIQUE (city, country)
);

-- -----------------------------------------------------------------------------
-- DIM_TIME : une ligne par heure distincte observée (arrondie à l'heure pleine)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_time (
    time_id       SERIAL PRIMARY KEY,
    full_datetime TIMESTAMPTZ NOT NULL,
    date          DATE NOT NULL,
    hour          SMALLINT NOT NULL,
    day_of_week   SMALLINT NOT NULL,
    day_name      VARCHAR(10) NOT NULL,
    is_weekend    BOOLEAN NOT NULL,
    day           SMALLINT NOT NULL,
    month         SMALLINT NOT NULL,
    year          SMALLINT NOT NULL,
    UNIQUE (full_datetime)
);

-- -----------------------------------------------------------------------------
-- FACT_AIR_QUALITY : une ligne par observation (ville x heure)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_id       BIGSERIAL PRIMARY KEY,
    city_id       INTEGER NOT NULL REFERENCES dim_city(city_id),
    time_id       INTEGER NOT NULL REFERENCES dim_time(time_id),
    observed_at   TIMESTAMPTZ NOT NULL,
    aqi           SMALLINT,
    co            NUMERIC(10,3),
    no            NUMERIC(10,3),
    no2           NUMERIC(10,3),
    o3            NUMERIC(10,3),
    so2           NUMERIC(10,3),
    pm2_5         NUMERIC(10,3),
    pm10          NUMERIC(10,3),
    nh3           NUMERIC(10,3),
    UNIQUE (city_id, time_id)
);

-- Ré-exécution idempotente : on repart d'une base vide à chaque run
-- (RESTART IDENTITY réinitialise aussi les compteurs SERIAL/BIGSERIAL)
TRUNCATE TABLE fact_air_quality, dim_time, dim_city RESTART IDENTITY CASCADE;

CREATE INDEX IF NOT EXISTS idx_fact_city ON fact_air_quality(city_id);
CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_air_quality(time_id);
CREATE INDEX IF NOT EXISTS idx_dim_time_date ON dim_time(date);
