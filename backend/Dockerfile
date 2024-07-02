FROM python:3.12
LABEL maintainer="MAAS Commiters <maas-commiters@canonical.com>"

ARG VERSION=development
ENV VERSION ${VERSION}

# ensure python stdout and stderr streams are sent straight to terminal
# also ensure nothing is buffered and thus may never be written
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --user tox

# install/setup nginx for TLS
RUN apt update && apt install -y curl gnupg2 ca-certificates lsb-release debian-archive-keyring snapd
RUN curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/debian `lsb_release -cs` nginx" | tee /etc/apt/sources.list.d/nginx.list
RUN echo "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900\n" | tee /etc/apt/preferences.d/99nginx
RUN apt update && apt install -y nginx

# create app directory
WORKDIR /app

# Bundle app source
COPY . /app/

# Copy nginx configuration
RUN cp /app/dev.nginx.conf /etc/nginx/conf.d/msm.conf

# Make a self-signed certificate
RUN mkdir -p /root/certs
WORKDIR /root/certs
RUN openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out msm.crt -keyout msm.key -subj "/C=US/ST=CO/L=Denver/O=MAAS Dev Team/OU=MSM/CN=msm/emailAddress=msm@msm.com"
RUN chmod 400 msm.key
RUN systemctl enable nginx

RUN chmod +x /app/start-nginx-and-api.sh

# Expose ports
EXPOSE 8000
EXPOSE 443

#ENTRYPOINT ["tail", "-f", "/dev/null"]  # to keep it running for debugging
WORKDIR /app
ENTRYPOINT ["sh", "/app/start-nginx-and-api.sh"]
# CMD ./start-nginx-and-api.sh
