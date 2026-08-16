-- ============================================================
-- PLANTPULSE SQL ANALYTICS
-- ============================================================


-- ============================================================
-- 1. PLANT PRODUCTION PERFORMANCE
-- ============================================================

SELECT
    Plant,
    SUM(Target_Production) AS Target_Production,
    SUM(Actual_Production) AS Actual_Production,
    
    ROUND(
        SUM(Actual_Production) * 100.0
        / NULLIF(SUM(Target_Production), 0),
        2
    ) AS Production_Achievement

FROM production

GROUP BY Plant

ORDER BY Production_Achievement DESC;