# llmagent

### Prerequisite:
- Python 3.10+ or above

### How to Install

- Create .env file in the root directory and update variables as per your environment.
```bash
cp .env.example .env
```

- Create Python virtual environment: 
```bash
python -m venv /path/to/new/virtual/environment
```

- Activate venv: 
```bash
source ~/yourvenv/bin/activate
```

- Add packages via requirements.txt: 
```bash
pip install -r /path/to/requirements.txt
```

### How to run the backend:

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

## With Docker

### How to run the backend with Docker:

```bash
docker compose --env-file .env up -d
```

### How to rebuild container

```bash
docker compose --env-file .env up -d --build backend
```