# Performance & Practical Notes
# Since the sample data is tabular and strictly formatted, it seems likely that it might exist
# in a relational database as opposed to csv files. Under this case, the following SQL query
# should net the same desired output:

"""
WITH cte AS (
    SELECT 
    -- Get the parent or child gene from the relationship pair
        CASE dh.disease_id_child
            WHEN ${query} THEN dh.disease_id_parent
            ELSE dh.disease_id_child
            END AS candidate_id
    FROM disease_hierarchy AS dh
    WHERE dh.disease_id_child = ${query} OR dh.disease_id_parent = ${query}
)
SELECT COUNT(asn.gene_id)
FROM cte
INNER JOIN associations AS asn
    ON asn.disease_id = cte.candidate_id
-- remove duplicates
GROUP BY asn.gene_id
"""
