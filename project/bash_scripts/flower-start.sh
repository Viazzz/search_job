#!/bin/bash

worker_ready() {
    celery -A settings inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 1
done
>&2 echo 'Celery workers is available'

celery -A settings  \
    --broker="${CELERY_BROKER}" \
    flower --url_prefix=flower \
    --basic-auth="${CELERY_USER}":"${CELERY_PSWD}"