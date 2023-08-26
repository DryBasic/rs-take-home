import polars as pl


class AssociationValidator:
    """
    Object to validate single gene, disease pair queries.

    Could be enhanced with exception handling and explicit
    error messages when a pair fails the check
        - wrong gene or disease?
        - "Did you mean ___" suggestions

    Could also be modified to take gene, disease labels instead.
    """
    def __init__(self, associations: pl.DataFrame):
        self.valid_associations = associations

    def validate(self, gene_id: str, disease_id: str):
        query = (gene_id, disease_id)
        return query in self.valid_associations
    