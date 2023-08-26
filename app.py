"""
The following script executes upon the instructional README requirements:

> Write a Python application that takes as input:
>   1. list of gene-disease associations,
>   2. disease hierarchy,
>   3. single gene-disease association pair as a query
> 
> And should output the number of unique genes associated with the query disease 
> or any of its direct parent/child diseases, based on the input data.

Suggested enhancements (guided partially by the "Considerations" of the 
instructional README) can be found in this repository's README. 
"""
from utils import *

asn = pl.read_csv('data/example_associations.csv')
validator = AssociationValidator(asn)

valid = False
while not valid: 
    query_gene = input('Enter valid gene ID: ')
    query_disease = input('Enter valid disease ID: ')
    valid = validator.validate(query_gene, query_disease)

dh = pl.read_csv('data/example_disease_hierarchy.csv')
sql = pl.SQLContext()
sql.register('asn', asn)
sql.register('dh', dh)

# Depending on codebase, may be preferred to write this in polars statements
# as opposed to SQL (and move to  utils-like file)
result = sql.execute(f"""
    -- Get all direct parent/child relationships
    -- Also get self with UNION
    WITH cte AS (
        SELECT 
            CASE dh.disease_id_child
                WHEN '{query_disease}' THEN dh.disease_id_parent
                ELSE dh.disease_id_child
                END AS candidate_id
        FROM dh
        WHERE dh.disease_id_child = '{query_disease}' 
            OR dh.disease_id_parent = '{query_disease}'
        UNION SELECT '{query_disease}' AS candidate_id FROM dh
    )
    -- Join to associations to get gene_id; GROUP BY to remove duplicates
    SELECT COUNT(gene_id)
    FROM cte
    INNER JOIN asn ON asn.disease_id = cte.candidate_id
    GROUP BY gene_id
""").collect()

print(f'Number of associated genes: {result}')
