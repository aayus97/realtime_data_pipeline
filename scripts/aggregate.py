import os
from scripts.database import execute_query

def calculate_and_store_aggregates(df, file_path):
    """
    Calculates aggregated metrics (min, max, mean, std, median, count) and stores them in the database.
    """
    query = """
        INSERT INTO aggregated_metrics (device, metric, min_value, max_value, avg_value, std_dev, median_value, count, file_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    metrics = df.groupby("device").agg({
        "co": ["min", "max", "mean", "std", "median", "count"],
        "humidity": ["min", "max", "mean", "std", "median", "count"],
        "lpg": ["min", "max", "mean", "std", "median", "count"],
        "smoke": ["min", "max", "mean", "std", "median", "count"],
        "temp": ["min", "max", "mean", "std", "median", "count"],
    })
    metrics.columns = ["_".join(col) for col in metrics.columns]
    metrics.reset_index(inplace=True)

    data = []
    for _, row in metrics.iterrows():
        for metric in ["co", "humidity", "lpg", "smoke", "temp"]:
            data.append((
                row["device"], metric, row[f"{metric}_min"], row[f"{metric}_max"],
                row[f"{metric}_mean"], row[f"{metric}_std"], row[f"{metric}_median"],
                row[f"{metric}_count"], os.path.basename(file_path)
            ))

    execute_query(query, data)
