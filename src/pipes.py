import polars as pl
import re


def cast_date_to_timestamp(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Casts a date column to a timestamp.
    Parameters:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the date column to cast.
    Returns:
        pl.DataFrame: A DataFrame with the specified date column converted to a timestamp in
    """
    return df.with_columns(
        pl.col(column_name).str.to_datetime()
    )


def cast_to_boolean(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Casts a column to boolean values.
    Parameters:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the column to cast.
    Returns:
        pl.DataFrame: A DataFrame with the specified column converted to boolean values.
    """
    return df.with_columns(
        pl.col(column_name).cast(pl.Boolean)
    )


def check_minutes(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Checks if the values in a specified column are in valid (non-negative).
    Parameters:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.
    Returns:
        pl.DataFrame: A DataFrame with an additional boolean column indicating if the values are in minutes.
    """
    negative_count = (df[column_name] < 0).sum()
    if negative_count > 0:
        print(f"Warning: Found {negative_count} negative values in '{column_name}' column.")
    return df


def check_unique(df: pl.DataFrame, column_name: str) -> bool:
    """
    Checks if the values in a specified column are unique.
    Parameters:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the column to check.
    Returns:
        bool: True if the values are unique, False otherwise.
    """
    unique_count = df[column_name].n_unique()
    total_count = df.shape[0]
    if unique_count == total_count:
        print(f"All values in '{column_name}' are unique.")
    else:
        print(f"Found {total_count - unique_count} duplicate values in '{column_name}' column.")
    return df


def cast_to_flag(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Casts a boolean column to a flag (1 for True, 0 for False).
    Parameters:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the boolean column to cast.
    Returns:
        pl.DataFrame: A DataFrame with the specified boolean column converted to a flag.
    """
    return (
        df
        .with_columns(
            pl.col(column_name).cast(pl.Boolean).alias(f"{column_name}_flag")
        )
    )


def get_value_counts(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Gets value counts for a specified column in a DataFrame.
    Args:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the column to get value counts for.
    Returns:
        pl.DataFrame: A DataFrame containing the value counts for the specified column.
    """
    return (
        df.select(
            pl.col(column_name)
            .value_counts()
            .struct.unnest()
        )
        .group_by(column_name)
        .agg(pl.col('count').sum())
        .sort(by=column_name, descending=False)
    )


def normalize_text(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Normalizes Organization Name column text.
    Args:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the column to normalize.
    Returns:
        pl.DataFrame: The DataFrame with the normalized column.
    """
    STOP = ["LLC", "Co", "Inc", "Corp", "Ltd"]
    pattern = r"(?i)\b(?:%s)\b" % "|".join(map(re.escape, STOP))


    return (
    df
    .with_columns(
        pl.col(column_name)
        .str.replace_all(r"[^\w\s]", " ") # remove punctuation
        .str.replace_all(pattern, "")          # drop stop-words
        .str.replace_all(r"\s+", " ")          # collapse whitespace
        .str.replace_all("Appraisals", "Appraisal") # Remove trailing 's' from Appraisals
        .str.replace_all("Review", "Appraisal") # Remove trailing 's' from Appraisals
        .str.to_titlecase() # convert to title case
        .str.split(' ') # split into list of words   
        .list.join(' ') # join back into a string
        .str.strip_chars_end() # remove trailing whitespace
    )
)


def summary_stats(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    """
    Computes summary statistics for a specified column in a DataFrame.
    Args:
        df (pl.DataFrame): The input DataFrame.
        column_name (str): The name of the column to compute summary statistics for.
    Returns:
        pl.DataFrame: A DataFrame containing the summary statistics for the specified column.
    """
    return (
        df
        .select(
            pl.col(column_name).mean().alias('mean'),
            pl.col(column_name).median().alias('median'),
            pl.col(column_name).min().alias('min'),
            pl.col(column_name).max().alias('max'),
            pl.col(column_name).std().alias('std')
        )
        .unpivot(variable_name="metric", value_name="value")
    )