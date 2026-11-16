-- showTelemetry

SELECT * FROM live_driver_telemetry
WHERE session_time = (SELECT MAX(session_time) FROM live_driver_telemetry)
LIMIT 5;
