WITH locations AS (
    SELECT
        sign_id,
        ward_no
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE speed_limit = 30
      AND end_date IS NULL
),

observed_locations AS (
    SELECT DISTINCT
        sign_id
    FROM 'data/processed/stationary-2026.parquet'
)

SELECT
    COUNT(*) AS active_30km_locations,
    COUNT(o.sign_id) AS locations_with_2026_data,
    COUNT(*) - COUNT(o.sign_id) AS locations_without_2026_data
FROM locations l
LEFT JOIN observed_locations o
    ON l.sign_id = o.sign_id;