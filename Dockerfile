# Compiler
FROM python:3.10 as compiler

ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

RUN pip install python-multipart

# Runner
FROM python:3.10 as runner

WORKDIR /code

COPY --from=compiler /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY ./app /code/app

COPY ./.env /code/.env

WORKDIR /code/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]