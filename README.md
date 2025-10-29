# lenka

An index of useful resources for people interested in Linked Data in Norway

## Setting up

It uses [Poetry](https://python-poetry.org/) to handle dependencies:

`poetry install`

## Run locally

`poetry run python3.12 main.py`

## Deployments

Vercel handles the building necessary for the various resources. (For this reason, you need to remember to update
_both_ pyproject.toml and requirements.txt when changing dependencies.)

This is a handy command to export dependencies from Poetry to requirements.txt:

`poetry export -f requirements.txt --output requirements.txt`

You can also test the build by running locally using [uv](https://docs.astral.sh/uv/) instead:

`uv run main.py`
