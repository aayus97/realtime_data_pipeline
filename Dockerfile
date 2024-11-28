# Use an official Python image as the base
FROM python:3.10-slim

ENV PYTHONPATH /app


# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose any necessary ports (if applicable)
EXPOSE 9092 6379

# Define the default command for the container
CMD ["celery", "-A", "worker.tasks", "worker", "--loglevel=info"]

# Run the Kafka consumer script as part of the worker package

#CMD ["python", "-m", "worker.kafka_consumer"]

