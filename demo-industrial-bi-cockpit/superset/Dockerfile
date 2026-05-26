ARG SUPERSET_BASE_IMAGE=apache/superset:latest
FROM ${SUPERSET_BASE_IMAGE}

USER root
COPY superset/bootstrap/build-language-packs.py /tmp/build-language-packs.py
RUN pip install --no-cache-dir --target /app/.venv/lib/python3.10/site-packages psycopg2-binary
RUN /app/.venv/bin/python /tmp/build-language-packs.py && rm /tmp/build-language-packs.py
USER superset
