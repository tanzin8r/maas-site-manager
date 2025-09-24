#!/bin/bash

if [[ -n "$TEMPORAL_TLS_ROOT_CAS" ]]; then
    echo "TEMPORAL_TLS_ROOT_CAS is set, need to install the CA in the system"
    echo "$TEMPORAL_TLS_ROOT_CAS" | base64 -d > /usr/local/share/ca-certificates/temporal.crt
    update-ca-certificates
fi

/bin/msm-worker
