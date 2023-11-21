# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9

# Copy local code to the container image.
ENV APP_HOME /lt2315
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -r requirements.txt

EXPOSE 2319

CMD python app.py
