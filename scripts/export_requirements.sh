#!/usr/bin/env bash

# Export dependencies installed with Poetry to requirements files that can be
# used with pip install
# https://dealroom.slite.com/app/docs/ihptWTKm4tjRWb

poetry export --output requirements.txt --without-hashes
sed -e 's/ *;.*$//g' requirements.txt > requirements-temp.txt
mv requirements-temp.txt requirements.txt

poetry export --with dev --output requirements-dev.txt --without-hashes
sed -e 's/ *;.*$//g' requirements-dev.txt > requirements-dev-temp.txt
mv requirements-dev-temp.txt requirements-dev.txt
