WITH speed_data AS (
    SELECT
        sign_id,
        CAST(
            regexp_extract(speed_bin, '\[(\d+),', 1)
            AS INTEGER
        ) AS speed_lower_bound,
        volume
    FROM 'data/processed/stationary-2026.parquet'
),

locations AS (
    SELECT
        sign_id,
        address,
        speed_limit,
        ward_no
    FROM 'data/processed/watch_your_speed_locations.parquet'
    WHERE speed_limit = 30
      AND end_date IS NULL
)

SELECT
    l.sign_id,
    l.address,
    l.speed_limit,
    l.ward_no,

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
        / NULLIF(SUM(s.volume), 0),
        2
    ) AS elevated_speed_pct

FROM speed_data s

JOIN locations l
    ON s.sign_id = l.sign_id

GROUP BY
    l.sign_id,
    l.address,
    l.speed_limit,
    l.ward_no

ORDER BY
    l.ward_no,
    l.sign_id;