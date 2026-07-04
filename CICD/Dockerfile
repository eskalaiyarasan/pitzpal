FROM docker.io/library/python:3.14-slim

# Install git and openssh-client (required for cloning)
RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

# Add GitHub to known hosts so SSH doesn't prompt to confirm the fingerprint
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

WORKDIR /app

# 1. Clone the private repository into the completely empty /app directory
#RUN --mount=type=ssh git clone git@github.com:eskalaiyarasan/pitzpal.git .
#RUN git checkout dontrun
# 1. Clone the specific branch 'dontrun' directly into the empty /app folder
RUN --mount=type=ssh git clone -b dontrun --single-branch git@github.com:eskalaiyarasan/pitzpal.git .

# 2. Install pipenv and project dependencies from the freshly cloned Pipfile
RUN pip install --no-cache-dir pipenv
RUN pipenv install --system --deploy

# 3. Copy your local entrypoint script into the container and make it executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
