# Considerations

 #### 1) What should be done about inconsistent or corrupted data/queries?

Different approaches can be taken depending on who the target end user is, and what the frequency of use will be:

* If the queries are to be provided en masse via a file, the parameters in the file should be QC'd (check if exists in database). Exceptions where an inappropriate parameter was passed should be handled to return an error code but allow for computation of the valid queries.

* If the queries are to be performed *infrequently* by a human user, a simple UI can be created to restrict the user to valid query parameters only.

 #### 2) How would you optimize the solution for a large number of gene-disease queries?



 #### 3) Parallelization? Caching?

 If the size of tables holding associations and hierarchies become sufficently large, the data and tasks can be parallelized. The easiest solution might be to use `Spark` (optimizing performance will likely require experimentation with `n` partitions). 

 SQL engines by default perform some level of parallelism (although not exactly "fine-tune-able"). There exists broad band of data sizes where the SQL engine will optimize and execute faster than other solutions (especially with read/write onto other machines). Writing optimized functions/procedures is likely the lowest maintenance headache as well.

 *Disclaimer: I've never had to work with data so large that it merited a separate computer server. I'm heavily biased towards offloading as much complexity onto the SQL host.*



***

# Performance & Practical Notes

Since the sample data is tabular and strictly formatted, it seems likely that it might exist in a relational database as opposed to csv files. Under this case, the following SQL query should net the same desired output:

```
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
```

However, this approach places all computational strain on the database host. The decision of where the transformation should be performed depends highly on the expected size of the data, frequency of transformation, and the coupling and resourcing of storage and compute. It may be easier to handle unique caching logic on a compute server decoupled from the database host. 