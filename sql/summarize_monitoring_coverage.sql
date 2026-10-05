WITH locations AS (
    SELECT sign_id
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE speed_limit = 30
      AND end_date IS NULL
      AND ward_no IS NOT NULL
),

daily_coverage AS (
    SELECT
        s.sign_id,
        COUNT(DISTINCT CAST(s.datetime_bin AS DATE))
            AS days_observed,
        SUM(s.volume) AS total_vehicles
    FROM 'data/processed/stationary-2026.parquet' s
    JOIN locations l
        ON s.sign_id = l.sign_id
    GROUP BY s.sign_id
)

SELECT
    CASE
        WHEN days_observed <= 7 THEN '1–7 days'
        WHEN days_observed <= 30 THEN '8–30 days'
        WHEN days_observed <= 90 THEN '31–90 days'
        WHEN days_observed <= 180 THEN '91–180 days'
        ELSE '181+ days'
    END AS coverage_group,
    COUNT(*) AS number_of_locations,
    SUM(total_vehicles) AS total_vehicles
FROM daily_coverage
GROUP BY coverage_group
ORDER BY MIN(days_observed);