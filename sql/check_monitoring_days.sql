SELECT
    sign_id,
    COUNT(DISTINCT CAST(datetime_bin AS DATE)) AS days_observed,
    SUM(volume) AS total_vehicles
FROM 'data/processed/stationary-2026.parquet'
GROUP BY sign_id
ORDER BY days_observed;