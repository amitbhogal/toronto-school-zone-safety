WITH locations AS (
    SELECT
        sign_id,
        ward_no,
        address,
        speed_limit
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE speed_limit = 30
      AND end_date IS NULL
      AND ward_no IS NOT NULL
),

speed_data AS (
    SELECT
        sign_id,
        CAST(datetime_bin AS DATE) AS observation_date,
        CAST(
            regexp_extract(speed_bin, '\[(\d+),', 1)
            AS INTEGER
        ) AS speed_lower_bound,
        volume
    FROM 'data/processed/stationary-2026.parquet'
),

location_metrics AS (
    SELECT
        l.sign_id,
        l.ward_no,
        l.address,
        COUNT(DISTINCT s.observation_date) AS days_observed,
        SUM(s.volume) AS total_vehicles,
        SUM(
            CASE
                WHEN s.speed_lower_bound >= l.speed_limit + 10
                THEN s.volume
                ELSE 0
            END
        ) AS elevated_speed_vehicles
    FROM locations l
    JOIN speed_data s
        ON l.sign_id = s.sign_id
    GROUP BY l.sign_id, l.ward_no, l.address
)

SELECT
    sign_id,
    ward_no,
    address,
    days_observed,
    total_vehicles,
    ROUND(
        100.0 * elevated_speed_vehicles
        / NULLIF(total_vehicles, 0),
        2
    ) AS speeding_percentage
FROM location_metrics
WHERE days_observed < 181
ORDER BY days_observed, ward_no;