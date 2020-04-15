#!/usr/bin/env bash

PROD_ENV_FILE=prod.env
if [[ ! -f "$PROD_ENV_FILE" ]]; then
    echo "File doesn't exist '$PROD_ENV_FILE'"
    exit 1
fi
export $(cat "$PROD_ENV_FILE")
echo ${PATH}
envsubst < app.templ.yaml > app.yaml
gcloud --quiet app deploy app.yaml
rm app.yaml
