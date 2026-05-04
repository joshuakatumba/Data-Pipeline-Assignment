-- Q1: Top Inventors
-- Who has the most patents?
SELECT i.name, COUNT(r.patent_id) as total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY total_patents DESC
LIMIT 10;

-- Q2: Top Companies
-- Which companies own the most patents?
SELECT c.name, COUNT(r.patent_id) as total_patents
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id, c.name
ORDER BY total_patents DESC
LIMIT 10;

-- Q3: Countries
-- Which countries produce the most patents?
SELECT i.country, COUNT(DISTINCT r.patent_id) as total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.country
ORDER BY total_patents DESC;

-- Q4: Trends Over Time
-- How many patents are created each year?
SELECT year, COUNT(patent_id) as total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year;

-- Q5: JOIN Query
-- Combine patents with inventors and companies
SELECT p.patent_id, p.title, i.name as inventor_name, c.name as company_name
FROM patents p
LEFT JOIN relationships r ON p.patent_id = r.patent_id
LEFT JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id
LIMIT 20;

-- Q6: CTE Query (WITH statement)
-- Break a complex query into steps. Let's find inventors who have more than the average number of patents.
WITH InventorCounts AS (
    SELECT i.inventor_id, i.name, COUNT(r.patent_id) as total_patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id, i.name
),
AveragePatents AS (
    SELECT AVG(total_patents) as avg_patents FROM InventorCounts
)
SELECT ic.name, ic.total_patents
FROM InventorCounts ic, AveragePatents ap
WHERE ic.total_patents > ap.avg_patents
ORDER BY ic.total_patents DESC
LIMIT 10;

-- Q7: Ranking Query
-- Rank inventors using window functions
SELECT 
    name,
    COUNT(r.patent_id) as total_patents,
    RANK() OVER (ORDER BY COUNT(r.patent_id) DESC) as inventor_rank
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
LIMIT 20;

-- Q8: Advanced Analysis - Patent Categories
-- Which patent classifications have the most patents?
SELECT classification, COUNT(patent_id) as total_patents
FROM patents
WHERE classification IS NOT NULL
GROUP BY classification
ORDER BY total_patents DESC
LIMIT 10;
