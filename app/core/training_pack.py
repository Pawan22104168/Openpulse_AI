from typing import Dict, List
from app.db.cache import get_cached_query_result
from app.sql.executor import execute_sql
from app.core.superset_client import fetch_chart_sql, fetch_dataset_columns

def build_training_pack(dashboard_metadata: Dict) -> Dict:
    """
    Build a training pack for RAG agent from dashboard metadata.

    Returns a dictionary containing:
    - ddl: list of CREATE TABLE statements (or table schema)
    - joins: inferred join relationships
    - chart_sqls: SQL for each chart
    - sample_rows: sample data from each dataset
    """
    training_pack = {
        "ddl": [],
        "joins": [],
        "chart_sqls": [],
        "sample_rows": []
    }

    charts = dashboard_metadata.get("charts", [])
    datasets = dashboard_metadata.get("datasets", [])

    # -----------------------------
    # Step 1: Extract chart SQLs
    # -----------------------------
    for chart in charts:
        chart_id = chart.get("id")
        sql = fetch_chart_sql(chart_id)
        if sql:
            training_pack["chart_sqls"].append({"chart_id": chart_id, "sql": sql})

    # -----------------------------
    # Step 2: Extract dataset schema (DDL) and sample rows
    # -----------------------------
    for dataset in datasets:
        dataset_id = dataset.get("id")
        columns = fetch_dataset_columns(dataset_id)
        if columns:
            # Create a pseudo-DDL
            ddl_stmt = f"TABLE {dataset.get('table_name', dataset_id)} (\n"
            ddl_stmt += ",\n".join([f"  {col['name']} {col['type']}" for col in columns])
            ddl_stmt += "\n)"
            training_pack["ddl"].append(ddl_stmt)

            # Fetch sample rows with caching
            sample_sql = f"SELECT * FROM {dataset.get('table_name', dataset_id)} LIMIT 5"
            sample_rows = get_cached_query_result(sample_sql)
            if not sample_rows:
                sample_rows = execute_sql(sample_sql)
            training_pack["sample_rows"].append({"dataset_id": dataset_id, "rows": sample_rows})

    # -----------------------------
    # Step 3: Infer join relationships (simple heuristic)
    # -----------------------------
    joins = []
    for i, ds1 in enumerate(datasets):
        for j, ds2 in enumerate(datasets):
            if i >= j:
                continue
            # Simple heuristic: common column names
            cols1 = set([col["name"] for col in ds1.get("columns", [])])
            cols2 = set([col["name"] for col in ds2.get("columns", [])])
            common_cols = cols1 & cols2
            for col in common_cols:
                joins.append({
                    "left_table": ds1.get("table_name", ds1.get("id")),
                    "right_table": ds2.get("table_name", ds2.get("id")),
                    "column": col
                })
    training_pack["joins"] = joins

    return training_pack
