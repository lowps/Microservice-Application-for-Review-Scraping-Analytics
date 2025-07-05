# Specify Parent Image
FROM python:3.10.4-buster

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# Prevents Python from buffering stdout and stderr; aids in logging and debugging
ENV PYTHONBUFFERED=1

# install system dependencies
RUN apt-get update && apt-get install -y netcat net-tools nano


# Set the working directory within the container to "/app" for subsequent commands
WORKDIR /app

COPY i_app/requirements.txt .

#Install dependencies (execute any command)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code inside ROOT directory "app"
COPY a_sourceCode/ a_sourceCode/
COPY b_utils/ b_utils/
COPY c_logs/ c_logs/
COPY d_static/ d_static/
COPY e_databaseSchemaStatic/ e_databaseSchemaStatic/
COPY f_data/ f_data/
COPY i_app/ i_app/

WORKDIR /app/i_app

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh


ENTRYPOINT ["./entrypoint.sh"]


