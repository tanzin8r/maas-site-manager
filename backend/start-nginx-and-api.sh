#!/bin/sh
if [ ${USE_NGINX_TLS_PROXY} -ne 0 ]; then
    /usr/sbin/nginx &
fi
python -m tox run -re api