FROM python:alpine3.15

# Required packages for poetry and psycop
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

RUN pip install poetry --quiet
WORKDIR /code
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi
COPY . /code
