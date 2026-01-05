FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN pip install -U pip && pip install uv && uv sync --frozen

COPY . .
EXPOSE 8000
CMD ["uvicorn", "carrot.main:app", "--host", "0.0.0.0", "--port", "8000"]
