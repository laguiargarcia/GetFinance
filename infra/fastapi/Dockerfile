FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.30.6 duckdb==1.5.2 duckdb-engine==0.13.2 openpyxl==3.1.2
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
