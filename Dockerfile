# Use the official Python 3.8 image
FROM python:3.9-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create the notion_pages and chroma_db directories inside the container
RUN mkdir -p /app/notion_pages /app/chroma_db

# Copy the notion2vector directory into the container
COPY notion2vector/ .

# Expose port 80 for the API
EXPOSE 80

# Command to run the application
CMD ["python", "main.py"]
