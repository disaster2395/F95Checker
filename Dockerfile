FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BIND_HOST=0.0.0.0 \
    BIND_PORT=8069

WORKDIR /app

COPY requirements-indexer.txt ./
RUN pip install --no-cache-dir -r requirements-indexer.txt

COPY indexer-main.py ./
COPY indexer/ ./indexer/
COPY common/ ./common/
COPY external/error.py external/weakerset.py ./external/
COPY modules/colors.py ./modules/

USER 10001:10001

EXPOSE 8069

CMD ["python", "indexer-main.py"]
