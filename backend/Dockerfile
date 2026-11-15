FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.runtime.lock pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir -r requirements.runtime.lock && pip install --no-cache-dir --no-deps .
COPY alembic.ini ./
COPY migrations ./migrations
RUN useradd --create-home --uid 10001 eduops
USER eduops
EXPOSE 8000
CMD ["python", "-m", "app", "--host", "0.0.0.0", "--port", "8000"]
