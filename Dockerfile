FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY policies ./policies
COPY fixtures ./fixtures
COPY evals ./evals
RUN pip install --no-cache-dir .
RUN addgroup --system policydesk && adduser --system --ingroup policydesk policydesk \
    && chown -R policydesk:policydesk /app
USER policydesk
EXPOSE 8000
CMD ["uvicorn", "policydesk.api:app", "--host", "0.0.0.0", "--port", "8000"]
