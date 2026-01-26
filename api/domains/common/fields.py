from sqlalchemy import Column, ForeignKey


def fk_cascade(foreign_key: str, cascade: bool = True, **kwargs) -> Column:
    """Create a ForeignKey column with optional CASCADE delete."""
    fk_args = {"ondelete": "CASCADE"} if cascade else {}
    return Column(ForeignKey(foreign_key, **fk_args), **kwargs)
