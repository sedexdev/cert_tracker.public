# base image
FROM python:slim-bullseye

# create user to run the app
RUN adduser --system --uid 1001 app

# set working directory
WORKDIR /home/app/src

# set Python specific env vars
ENV PYTHONPATH=/home/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# copy application file to container
COPY --chown=app:app main.py .

# switch to app user
USER app

# run the application
CMD ["python3", "main.py"]

