# ------------ Base image ---------------
FROM python:3.11-slim AS base
WORKDIR /app

# Copy shared requirements file
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt


# ------------ Backend stage ------------
FROM base AS backend
WORKDIR /app
COPY app/backend/ /app

CMD ["python", "main.py"]


# ------------ Streamlit stage ----------
FROM base AS streamlit
WORKDIR /app
COPY app/streamlit/ /app

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
