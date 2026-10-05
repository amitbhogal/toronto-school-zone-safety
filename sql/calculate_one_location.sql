SELECT
    sign_id,

    SUM(volume) AS total_vehicles,

    SUM(
        CASE
            WHEN speed_bin >= '[50,55)'
            THEN volume
            ELSE 0
        END
    ) AS elevated_speed_vehicles

FROM 'data/processed/stationary-2026.parquet'

WHERE sign_id = 302

GROUP BY sign_id;