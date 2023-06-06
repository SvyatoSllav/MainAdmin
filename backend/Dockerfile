FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend/

# Install dependencies
COPY pyproject.toml /backend/
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /backend/

EXPOSE 8000

# Start the app
CMD ["gunicorn", "config.wsgi:application", "--reload", "--bind", "0.0.0.0:8000", "--workers", "3"] 