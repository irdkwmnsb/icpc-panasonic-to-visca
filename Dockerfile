FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app


# Make port 80 available to the world outside this container
EXPOSE 80

ENTRYPOINT ["uvicorn", "proxy:app", "--port", "80", "--host", "0.0.0.0"]