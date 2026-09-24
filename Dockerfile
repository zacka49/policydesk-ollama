FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY policies ./policies
COPY fixtures ./fixtures
COPY evals ./evals
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "policydesk.api:app", "--host", "0.0.0.0", "--port", "8000"]
