################
## BUILD NODE ##
################

# use NOdeJS base image
FROM node:18-bookworm-slim AS node_builder

# update the image
RUN apt update

# create app user account
RUN adduser --system --uid 1001 app

# set working directory to app user
WORKDIR /home/app/src

# copy project
COPY --chown=app:app . .

# minify Tailwind CSS
RUN npm init -y \
    && npm i \
    && npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

#######################
## BUILD PYTHON SLIM ##
#######################

FROM python:3.12-slim-bookworm

# update the image
RUN apt update

# create app user account
RUN adduser --system --uid 1001 app

# set working directory to app user
WORKDIR /home/app/src

# set environment variables
ENV PYTHONPATH=/home/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# copy project files from builders
COPY --from=node_builder --chown=app:app /home/app/src .

# install pip dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pip-audit && pip-audit

# change to the app user
USER app

# run app start command
CMD [ "flask", "run", "--host", "0.0.0.0" ]
