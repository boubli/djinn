"""
Data & ML - Pandas, Spark, Jupyter.
"""
from typing import Optional


class PandasPlugin:
    """Pandas data manipulation code generator."""
    
    SYSTEM_PROMPT = """You are a Pandas expert. Generate Python pandas code snippets.

Examples:
- "read csv" -> df = pd.read_csv('file.csv')
- "filter rows" -> df[df['column'] > 10]
- "group by" -> df.groupby('category').mean()
- "merge" -> pd.merge(df1, df2, on='key')"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class SparkPlugin:
    """Apache Spark command generator."""
    
    SYSTEM_PROMPT = """You are a Spark expert. Generate spark-submit or PySpark commands.

Examples:
- "submit job" -> spark-submit --master local[*] script.py
- "read parquet" -> df = spark.read.parquet('data/')
- "sql query" -> spark.sql('SELECT * FROM table')"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class JupyterPlugin:
    """Jupyter notebook command generator."""
    
    SYSTEM_PROMPT = """You are a Jupyter expert. Generate Jupyter commands.

Examples:
- "start notebook" -> jupyter notebook
- "start lab" -> jupyter lab
- "convert to html" -> jupyter nbconvert --to html notebook.ipynb
- "list kernels" -> jupyter kernelspec list"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
