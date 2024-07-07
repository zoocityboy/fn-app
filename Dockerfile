# Using lightweight alpine image
FROM python:3.12-alpine
# Set up environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set up environment variables for Flask
ARG FLASK_ENV=production
ARG FLASK_API_KEY=flaskMySecretKey
ENV FLASK_API_KEY=$FLASK_API_KEY
# Installing packages
RUN apk update
RUN pip install --no-cache-dir pipenv

# Defining working directory and adding source code
WORKDIR /app
COPY Pipfile Pipfile.lock bootstrap.sh ./
COPY src ./src

# Install API dependencies
RUN pipenv install --system --deploy

# Start app
EXPOSE 5000
ENTRYPOINT ["/app/bootstrap.sh"]
