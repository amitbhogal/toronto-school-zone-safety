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
),

location AS (
    SELECT
        sign_id,
        speed_limit
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE sign_id = 302
)

SELECT
    s.sign_id,
    l.speed_limit,
    l.speed_limit + 10 AS threshold,
    SUM(s.volume) AS total_vehicles,

    SUM(
        CASE
            WHEN s.speed_lower_bound >= l.speed_limit + 10
            THEN s.volume
            ELSE 0
        END
    ) AS elevated_speed_vehicles,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN s.speed_lower_bound >= l.speed_limit + 10
                THEN s.volume
                ELSE 0
            END
        )
        / SUM(s.volume),
        2
    ) AS elevated_speed_pct

FROM speed_data s
JOIN location l
    ON s.sign_id = l.sign_id

GROUP BY
    s.sign_id,
    l.speed_limit;