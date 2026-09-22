FROM python:3.14-slim

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app

RUN pip install --no-cache-dir . \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + \
    && find /app -type d -name "*.egg-info" -exec rm -rf {} +

ENV PYTHONPATH=/app/app
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]