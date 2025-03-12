FROM python:3.9-slim

WORKDIR /app

# Copy only the requirements file first to leverage Docker caching
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start both the Streamlit and FastAPI servers
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 8501 --server.address 0.0.0.0"] 