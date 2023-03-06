FROM python:3.10
LABEL maintainer="MAAS Commiters <maas-commiters@canonical.com>"

ARG VERSION=development
ENV VERSION ${VERSION}

# ensure python stdout and stderr streams are sent straight to terminal
# also ensure nothing is buffered and thus may never be written
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --user tox

# create app directory
WORKDIR /app

# Bundle app source
COPY . /app/

# Expose port
EXPOSE 8000

#ENTRYPOINT ["tail", "-f", "/dev/null"]  # to keep it running for debugging
ENTRYPOINT ["python", "-m", "tox", "-e", "run", "run"]
