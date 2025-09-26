from pydantic import BaseModel, Field
from typing import List, Optional

class Column(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class Dataset(BaseModel):
    id: int
    table_name: str
    columns: List[Column] = Field(default_factory=list)
    description: Optional[str] = None

class Chart(BaseModel):
    id: int
    name: str
    dataset_id: int
    viz_type: Optional[str] = None
    sql: Optional[str] = None
    description: Optional[str] = None

class Dashboard(BaseModel):
    id: int
    name: str
    charts: List[Chart] = Field(default_factory=list)
    datasets: List[Dataset] = Field(default_factory=list)
    description: Optional[str] = None
