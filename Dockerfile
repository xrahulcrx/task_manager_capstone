FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

# Create DB folder inside container
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "task_man.main:app", "--host", "0.0.0.0", "--port", "8000"]
