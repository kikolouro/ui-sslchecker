#!/bin/sh
gunicorn main:app -w 2 --threads 2 --reload -b 0.0.0.0:80