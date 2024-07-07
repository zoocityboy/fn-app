#!/bin/sh
docker build --build-arg FLASK_API_KEY="secretCustomKey" -t zoocityboy/fn-app:v1.0.0 .
