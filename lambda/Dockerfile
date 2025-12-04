FROM public.ecr.aws/lambda/python:3.12

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}/
COPY lambda/handler.py ${LAMBDA_TASK_ROOT}/
COPY pyproject.toml ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install --no-cache-dir boto3 deepdiff click structlog

# Set handler
CMD ["handler.handler"]
