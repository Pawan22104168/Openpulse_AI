from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class JoinInfo(BaseModel):
    left_table: str
    right_table: str
    column: str

class SchemaAnalysis(BaseModel):
    joins: List[JoinInfo]
    columns: Dict[str, Dict[str, str]]  # table_name -> { column_name: column_type }

def analyze_schema(datasets: List[Dict[str, Any]]) -> SchemaAnalysis:
    """
    Analyze datasets to extract:
    - Join relationships based on common columns
    - Column summaries (column types)
    
    Returns a SchemaAnalysis Pydantic model.
    """
    analysis = {
        "joins": [],
        "columns": {}
    }

    # Build column summary
    for dataset in datasets:
        table_name = dataset.get("table_name") or str(dataset.get("id"))
        if not table_name:
            continue

        columns = dataset.get("columns", [])
        analysis["columns"][table_name] = {}

        for col in columns:
            col_name = col.get("name")
            col_type = col.get("type", "UNKNOWN")
            if col_name:
                analysis["columns"][table_name][col_name] = col_type

    # Infer joins (simple heuristic: columns with same name in different tables)
    tables = list(analysis["columns"].keys())
    for i, t1 in enumerate(tables):
        for j, t2 in enumerate(tables):
            if i >= j:
                continue
            cols_t1 = set(analysis["columns"][t1].keys())
            cols_t2 = set(analysis["columns"][t2].keys())
            common_cols = cols_t1.intersection(cols_t2)
            for col in common_cols:
                analysis["joins"].append({
                    "left_table": t1,
                    "right_table": t2,
                    "column": col
                })

    return SchemaAnalysis(**analysis)
