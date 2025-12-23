# Use Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a non-root user to run the app
RUN useradd -m appuser

# Set the working directory inside the container
WORKDIR /app

# Copy the backend project contents into the container at /app
COPY backend /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set permissions for static and media directories
RUN mkdir -p /app/staticfiles /app/media && chown -R appuser:appuser /app/staticfiles /app/media

# Change ownership of the /app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run on container start
CMD ["gunicorn", "image_service.wsgi:application", "--bind", "0.0.0.0:8000"]
