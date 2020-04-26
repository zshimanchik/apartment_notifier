#!/usr/bin/env bash

PROD_ENV_FILE=prod.env
if [[ ! -f "$PROD_ENV_FILE" ]]; then
    echo "File doesn't exist '$PROD_ENV_FILE'"
    exit 1
fi
export $(cat "$PROD_ENV_FILE")

if [[ -z "${PROJECT_ID}" ]]; then
    echo "You need to specify PROJECT_ID"
    exit 1
fi

gcloud config set project "${PROJECT_ID}"
envsubst < app.templ.yaml > app.yaml
gcloud --quiet app deploy app.yaml
gcloud --quiet app deploy cron.yaml
rm app.yaml
