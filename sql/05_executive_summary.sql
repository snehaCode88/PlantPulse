-- ============================================
-- PLANTPULSE EXECUTIVE SUMMARY
-- ============================================

-- 1. Production achievement by plant

SELECT
    Plant,
    SUM(Target_Production) AS Total_Target,
    SUM(Actual_Production) AS Total_Actual,
    ROUND(
        SUM(Actual_Production) * 100.0
        / SUM(Target_Production),
        2
    ) AS Achievement_Percent
FROM production
GROUP BY Plant
ORDER BY Achievement_Percent ASC;


-- 2. Downtime by plant

SELECT
    Plant,
    ROUND(SUM(Downtime_Hours), 2) AS Total_Downtime_Hours
FROM downtime
GROUP BY Plant
ORDER BY Total_Downtime_Hours DESC;


-- 3. Main downtime problem

SELECT
    Machine,
    Downtime_Reason,
    ROUND(SUM(Downtime_Hours), 2) AS Total_Downtime_Hours
FROM downtime
WHERE Plant = 'Plant B'
GROUP BY Machine, Downtime_Reason
ORDER BY Total_Downtime_Hours DESC
LIMIT 5;


-- 4. Product quality performance

SELECT
    Product,
    SUM(Units_Produced) AS Units_Produced,
    SUM(Defective_Units) AS Defective_Units,
    ROUND(
        SUM(Defective_Units) * 100.0
        / SUM(Units_Produced),
        2
    ) AS Defect_Rate_Percent
FROM quality
GROUP BY Product
ORDER BY Defect_Rate_Percent DESC;