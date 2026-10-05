SELECT
    CAST(ward_no AS INTEGER) AS ward_no,
    COUNT(*) AS location_count
FROM read_parquet(
    'data/processed/watch_your_speed_locations.parquet'
)
WHERE end_date IS NULL
  AND speed_limit = 30
GROUP BY ward_no
ORDER BY ward_no;