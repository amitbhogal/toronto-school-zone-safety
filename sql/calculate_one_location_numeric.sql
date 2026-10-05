WITH speed_data AS (
    SELECT
        sign_id,
        CAST(
            regexp_extract(speed_bin, '\[(\d+),', 1)
            AS INTEGER
        ) AS speed_lower_bound,
        volume
    FROM 'data/processed/stationary-2026.parquet'
    WHERE sign_id = 302
)

SELECT
    sign_id,
    SUM(volume) AS total_vehicles,
    SUM(
        CASE
            WHEN speed_lower_bound >= 50
            THEN volume
            ELSE 0
        END
    ) AS elevated_speed_vehicles,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN speed_lower_bound >= 50
                THEN volume
                ELSE 0
            END
        ) / SUM(volume),
        2
    ) AS elevated_speed_pct

FROM speed_data

GROUP BY sign_id;