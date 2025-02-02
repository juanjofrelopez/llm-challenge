import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Drop rows with any missing values
    df.dropna(inplace=True)

    # Strip leading/trailing spaces from string columns
    str_columns = ['week_day', 'ticket_number', 'product_name']
    for col in str_columns:
        df[col] = df[col].str.strip()

    # Ensure numeric columns have valid positive values
    numeric_columns = ['quantity', 'unitary_price', 'total']
    for col in numeric_columns:
        df[col] = df[col].apply(lambda x: max(x, 0) if pd.notnull(x) else 0)

    # Convert 'hour' to a valid time format
    df['hour'] = pd.to_datetime(
        df['hour'], format='%H:%M', errors='coerce').dt.time
    # Drop rows where hour conversion failed
    df.dropna(subset=['hour'], inplace=True)

    return df
