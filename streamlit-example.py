import streamlit as st
from pathlib import Path
from utils import *

with st.sidebar:
    associations_path = st.text_input('Path to associations', value='./data/example_associations.csv')
    hierarchy_path = st.text_input('Path to hierarchies', value='./data/example_disease_hierarchy.csv')

asn = pl.read_csv(Path(__file__).parent / associations_path)
dh = pl.read_csv(Path(__file__).parent / hierarchy_path)

query_gene, query_disease = st.selectbox('Pick an association', options=asn.rows())

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
""").collect().item(0,0)

st.success(f'Number of associated genes: {result}')
