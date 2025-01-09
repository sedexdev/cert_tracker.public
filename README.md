# Cert Tracker

[![Lint and Test](https://github.com/sedexdev/cert_tracker/actions/workflows/test.yml/badge.svg)](https://github.com/sedexdev/cert_tracker/actions/workflows/test.yml)

# Overview

Cert Tracker let's you track all aspects of your next IT certification study progression. I've found that having study resources scattered around on various platforms (YouTube/Reddit/Udemy/Medium/DevTo etc.) leads to either text documents full of links, or annoying spreadsheets, or collections of OneNote notebooks, and it all gets a bit messy.

Wouldn't it be nice to have all your cert specific resources (courses/video content/articles/documentation) all in one place?

That's what this app is for. It is still in development so more features will be released in due time but currently the app allows you to:

- Work inside a local Docker container runtime environment with local PostgreSQL data storage
- Upload course links
- Add all course sections for tracking completion and flash card creation
- Upload video/article/documentation links in well organised sections
- Customise images for your resources
- Import resources into other certs
- Set exam dates
- Switch between light and dark mode

New features under development include:

- Configurable email reminders running up to exam day
- Plotly Dash graphical analysis dashboard to see your progress
- Cost analysis to see your cert spending
- In-app WYSIWYG text editor and file tree for managing notes
- An area for storing links to your practice exams
- Digital flash cards

Fork the repo if you are interested in contributing to this project, new suggestions are very welcome as well as code contributions.

# Prerequisites

- A system account with administrator privileges
- <code>git</code> - https://github.com/git-guides/install-git
- <code>docker</code> - https://docs.docker.com/engine/install/
- <code>docker compose</code> - https://docs.docker.com/compose/install/
- <code>wsl2</code> - https://learn.microsoft.com/en-us/windows/wsl/install (Windows only when using Docker Desktop)

# Getting started 

Clone the repo on to your local machine into a directory of your choice:

<code>git clone https://github.com/sedexdev/cert_tracker.git</code>

**Run the following commands in the project root** - <code>cert_tracker</code>

## Running app containers

- Mac/Linux: <code>sudo docker compose up -d</code></br>
- Windows: <code>docker compose up -d</code> (from admin prompt)

In your browser navigate to http://127.0.0.1:8181 to view the application once built.

## Stopping app containers

- Mac/Linux: <code>sudo docker compose stop</code></br>
- Windows: <code>docker compose stop</code> (from admin prompt)

## Teardown

If you want to destroy the local images run:

- Mac/Linux: <code>sudo docker compose down --rmi local</code></br>
- Windows: <code>docker compose down --rmi local</code> (from admin prompt)

If you also want to destroy the PostgreSQL database run:

- Mac/Linux: <code>sudo docker compose down --rmi local -v</code></br>
- Windows: <code>docker compose down --rmi local -v</code> (from admin prompt)

# Setup

## Secrets

Update the 2 .txt files under <code>cert_tracker/secrets</code> for the PostgreSQL database password and the Flask app secret:

- <code>cert_tracker/secrets/postgres-pw.txt</code>
- <code>cert_tracker/secrets/secret.txt</code>

**NOTE**: Despite this app runnging locally you should follow best practice and make these secrets complex, and avoid exposing them in public places.

# Open Graph Protocol

Where possible the application will query the URL used to create a <code>resource</code> and try to pull Open Graph data from the URL using the Python package <code>opengraph_py3</code>. When a site has metadata available through the protocol, form fields will auto-populate with images and other available information.

# Email reminder configuration

**In Progress**

# Change log

08/01/2025 - Uploaded v1.1.0 - Image file uploads [5db06a0](https://github.com/sedexdev/cert_tracker/commit/396b4aa80e8df66e1919d6c81675f06155db06a0)</br>
17/12/2024 - BUG FIX - MODULE_NOT_FOUND error during <code>npm</code> setup in <code>Dockerfile</code> [d657a0c](https://github.com/sedexdev/cert_tracker/commit/d657a0ce10e4e38b8623ef92b95b3df77a1ba2da)</br>
13/12/2024 - Uploaded v1.0.0

# License

[M.I.T](https://github.com/sedexdev/cert_tracker/blob/main/LICENSE)
