# ------------ Base image ---------------
FROM python:3.11-slim AS base
WORKDIR /app

# Create and set permissions for temp directory
RUN mkdir -p /tmp && chmod 1777 /tmp

# Copy shared requirements file
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt


# ------------ Backend stage ------------
FROM base AS backend
WORKDIR /app

# Ensure temp directory exists with correct permissions
RUN mkdir -p /tmp && chmod 1777 /tmp

COPY app/backend/ /app

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ------------ Streamlit stage ----------
FROM base AS streamlit
WORKDIR /app

# Ensure temp directory exists with correct permissions
RUN mkdir -p /tmp && chmod 1777 /tmp

# Copy entire project (needed because streamlit imports backend)
COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit/main.py", "--server.port=8501", "--server.address=0.0.0.0"]