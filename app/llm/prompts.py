"""
Predefined prompt templates for LLM-based RAG agent.
These templates are used to generate SQL + insights
based on retrieved dashboard metadata.
"""

SQL_INSIGHT_PROMPT = """
You are a SQL expert and data analyst.
Based on the following dashboard metadata, generate:
1. A single SQL query that could answer key metrics.
2. A brief natural-language insight.
Only produce syntactically correct SQL and a short insight.

Context:
{context_text}

Response format:
SQL:
<your SQL here>

Insight:
<short insight here>
"""
