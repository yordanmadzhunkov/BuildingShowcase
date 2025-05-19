# Fetching official base image for python
FROM python:3.10.13-alpine3.18

# Setting up the work directory
ENV APP_PATH=/opt/app
ENV APP_PORT=5000
WORKDIR $APP_PATH/

# Copy the current directory contents into the container at /app
COPY . $APP_PATH

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

RUN pip3 install --upgrade pip gunicorn    

# Make port 5070 available to the world outside this container
EXPOSE $APP_PORT


COPY gunicorn_starter.sh  /entrypoint/

# Run app.py when the container launches
ENTRYPOINT ["sh", "/entrypoint/gunicorn_starter.sh"]
