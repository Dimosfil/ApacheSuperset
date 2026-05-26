ARG SUPERSET_BASE_IMAGE=apache/superset:latest
FROM ${SUPERSET_BASE_IMAGE}

USER root
RUN pip install --no-cache-dir --target /app/.venv/lib/python3.10/site-packages psycopg2-binary
USER superset
