WITH locations AS (
    SELECT sign_id, ward_no, address
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE speed_limit = 30
      AND end_date IS NULL
),

observed_locations AS (
    SELECT DISTINCT sign_id
    FROM 'data/processed/stationary-2026.parquet'
)

SELECT
    l.ward_no,
    l.sign_id,
    l.address,
    CASE
        WHEN o.sign_id IS NULL THEN 'No matching records'
        ELSE 'Has records'
    END AS observation_status
FROM locations l
LEFT JOIN observed_locations o
    ON l.sign_id = o.sign_id
WHERE o.sign_id IS NULL
ORDER BY l.ward_no, l.sign_id;