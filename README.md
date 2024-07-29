# llmagent

# Prerequisite:
- Python 3.10+ or above
- Create Python virtual environment: 
```
python -m venv /path/to/new/virtual/environment
```
- Activate venv: 
```
source ~/yourvenv/bin/activate
```
- Add packages via requirements.txt: 
```
pip install -r /path/to/requirements.txt
```

# How to run the backend:
```
cd backend
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```
