FROM python:3.11-slim

WORKDIR /vault

COPY serve.py .
COPY serve-requirements.txt .

RUN python -m ensurepip --upgrade \
 && pip install --upgrade pip setuptools \
 && pip install -r serve-requirements.txt

CMD ["python", "serve.py"]
