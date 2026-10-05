SELECT
    sign_id,
    datetime_bin,
    speed_bin,
    volume
FROM 'data/processed/stationary-2026.parquet'
WHERE sign_id = 302
ORDER BY datetime_bin, speed_bin
LIMIT 50;