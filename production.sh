#!/bin/sh
export FLASK_APP=./src/index.py
pipenv run flask run -h 0.0.0.0
