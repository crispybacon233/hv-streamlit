import polars as pl


def filter_organization(df: pl.DataFrame, organization_name: str) -> pl.DataFrame:
    """
    Filters the DataFrame based on the organization name.

    Parameters:
    df (pl.DataFrame): The input DataFrame.
    organization_name (str): The organization name to filter by.

    Returns:
    pl.DataFrame: The filtered DataFrame.
    """
    if organization_name == '- All -':
        return df
    else:
        return df.filter(pl.col('organization_name').is_in(organization_name))


def filter_property_type(df: pl.DataFrame, property_type: str) -> pl.DataFrame:
    """
    Filters the DataFrame based on the property type.

    Parameters:
    df (pl.DataFrame): The input DataFrame.
    property_type (str): The property type to filter by.

    Returns:
    pl.DataFrame: The filtered DataFrame.
    """
    if property_type == '- All -':
        return df
    else:
        return df.filter(pl.col('property_type') == property_type)
    

def filter_loan_type(df: pl.DataFrame, loan_type: str) -> pl.DataFrame:
    """
    Filters the DataFrame based on the loan type.

    Parameters:
    df (pl.DataFrame): The input DataFrame.
    loan_type (str): The loan type to filter by.

    Returns:
    pl.DataFrame: The filtered DataFrame.
    """
    if loan_type == '- All -':
        return df
    else:
        return df.filter(pl.col('loan_type') == loan_type)


def filter_qc_version(df: pl.DataFrame, qc_version: str) -> pl.DataFrame:
    """
    Filters the DataFrame based on the QC version.

    Parameters:
    df (pl.DataFrame): The input DataFrame.
    qc_version (str): The QC version to filter by.

    Returns:
    pl.DataFrame: The filtered DataFrame.
    """
    if qc_version == '- All -':
        return df
    else:
        return df.filter(pl.col('qc_versions') == int(qc_version))