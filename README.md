
# Introduction

* `app.py` main solution 
    * `requirements.txt` pertains to this file (just `polars`)
* `streamlit-example.py` solution but using the `streamlit` framework for a UI
    * Requires installation of `streamlit` module
    * Can deploy locally after installation via `streamlit run streamlit-example.py` from the working directory

***

# Considerations

 #### 1) What should be done about inconsistent or corrupted data/queries?

The "AssociationValidator" object was written to confirm the provided query exists within the known set of associations. Under the current design where inputs are single pairs, this could also be replaced using a UI with restrictive drop-downs.

Can be very quickly done with `streamlit`:
```
import streamlit as st

query_gene, query_disease = st.selectbox('Pick an association', options=asn.rows())
```

However, practically speaking, such an application is unlikely to be used in a one-by-one approach. If the queries are to be provided en masse via a file, they could be validated en masse as well: 
```
SELECT gene_id, disease_id, 
    CASE val.gene_id
        WHEN NULL THEN 'Fail'
        ELSE 'Pass'
        END AS validation_result
FROM input
LEFT JOIN valid_associations AS val
    ON input.disease_id = val.disease_id
    AND input.gene_id = val.gene_id
```

 #### 2) How would you optimize the solution for a large number of gene-disease queries?

The validation can be optimized per the last section of consideration 1. Optimizing the computation itself might require using different tools that support parallelization (see consideration 3). 

The size of the data to query against is even more impactful than the number of queries. The optimal solution depends heavily on the coupling and resources of compute and storage. It is likely that for a broad range of data sizes, the most efficient solution may be to simply write a SQL function or procedure on the database host. If the database is constantly changing, this is highly recommended to minimize the need for constant cache refreshes on the machine sending the queries. 

 #### 3) Parallelization? Caching?

 If the sizes of the tables holding associations and hierarchies become sufficently large, the data and tasks can be parallelized for efficiency. The easiest solution might be to use `Spark` (optimizing performance will likely require experimentation with `n` partitions). Like `polars`, `PySpark` offers a SQL context so that the existing code can be almost fully reused.

 SQL engines by default perform some level of parallelism (although not exactly "fine-tune-able"). There exists a broad band of data sizes where the SQL engine will optimize and execute faster than other solutions (especially with read/write onto other machines). Writing optimized functions/procedures is likely the lowest maintenance headache as well.
 