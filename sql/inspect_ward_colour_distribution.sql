
WITH locations AS (
    SELECT sign_id, ward_no, speed_limit
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE speed_limit = 30
      AND end_date IS NULL
      AND ward_no IS NOT NULL
),

speed_bins AS (
    SELECT
        sign_id,
        CAST(
            regexp_extract(speed_bin, '\[(\d+),', 1)
            AS INTEGER
        ) AS speed_lower_bound,
        volume
    FROM 'data/processed/stationary-2026.parquet'
),

location_metrics AS (
    SELECT
        l.ward_no,
        l.sign_id,
        SUM(s.volume) AS total_vehicles,
        SUM(
            CASE
                WHEN s.speed_lower_bound >= l.speed_limit + 10
                THEN s.volume
                ELSE 0
            END
        ) AS elevated_speed_vehicles
    FROM locations l
    JOIN speed_bins s ON l.sign_id = s.sign_id
    GROUP BY l.ward_no, l.sign_id
),

ward_metrics AS (
    SELECT
        ward_no,
        COUNT(*) AS locations_with_data,
        SUM(total_vehicles) AS total_vehicles,
        AVG(
            100.0 * elevated_speed_vehicles
            / NULLIF(total_vehicles, 0)
        ) AS ward_percentage
    FROM location_metrics
    WHERE total_vehicles > 0
    GROUP BY ward_no
)

SELECT
    ward_no,
    locations_with_data,
    total_vehicles,
    ROUND(ward_percentage, 2) AS speeding_percentage
FROM ward_metrics
ORDER BY speeding_percentage;