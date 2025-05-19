#!/bin/bash

gunicorn --chdir $APP_PATH --bind 0.0.0.0:${APP_PORT} --reuse-port --reload main:app
