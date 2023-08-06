ARG PYTHON_VERSION
ARG ALPINE_VERSION
FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}
# Keep this below the FROM instruction
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG DJANGO_VERSION

RUN apk add --update bash gnupg1

RUN pip install --upgrade pip
RUN pip install coverage coveralls flake8 python-gnupg
RUN pip install "${DJANGO_VERSION}" || \
    echo >&2 "You must pass DJANGO_VERSION in the build arguments: --build-arg DJANGO_VERSION=..."

RUN mkdir /code

WORKDIR /code
