# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . .


# Expose the port that the Flask app will run on
EXPOSE 80

CMD ["python", "app.py"]
