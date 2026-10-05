SELECT
    speed_bin,
    regexp_extract(speed_bin, '\[(\d+),', 1) AS speed_lower_bound,
    SUM(volume) AS vehicles
FROM 'data/processed/stationary-2026.parquet'
WHERE sign_id = 302
GROUP BY speed_bin
ORDER BY CAST(regexp_extract(speed_bin, '\[(\d+),', 1) AS INTEGER);