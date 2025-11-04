# Use Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Spaces uses 7860 by default)
EXPOSE 7860

# Set environment variable for Flask
ENV PORT=7860

# Run your app
CMD ["python", "app.py"]
