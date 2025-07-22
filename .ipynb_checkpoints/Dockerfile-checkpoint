FROM python:3.10-slim

# Setting working directory
WORKDIR /app

COPY requirements.txt .

# Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

# Copying entire project
COPY . .

# Expose FastAPI's port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
