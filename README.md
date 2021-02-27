# Welcome Spaces REST API Backend

[![CircleCI](https://circleci.com/gh/decagonhq/bouncer-restapi/tree/master.svg?style=svg&circle-token=f84852fd9b9ee23b40fdfcf2d2e38dc5f65cb1e2)](https://circleci.com/gh/decagonhq/bouncer-restapi/tree/master)

Squad 3 - REST API backend for [234Spaces Application](https://234spaces.com/)

## Technologies

* [Python 3.7](https://python.org) : Base development programming language
* [Bash Scripting](https://www.codecademy.com/learn/learn-the-command-line/modules/bash-scripting) : Create convinient script for easy development experience
* [PostgreSQL](https://www.postgresql.org/) : Application backing relational databases for both staging and production environments
* [Django Framework](https://www.djangoproject.com/) : Host development framework built on top of python
* [Django Rest Framework](https://www.django-rest-framework.org/) : Provides API development tools for easy API development
* [CircleCI]() : Continous Integration and Deployment
* [Docker Engine and Docker Compose](https://www.docker.com/) : Containerization of the application and services orchestration

## Getting Started

Few things you need to setup to get started, set up a virtual environment majorly for isolating installs, create a `.env` file from the example file and finally install all requirements in the `requirements.txt` files within the virtual environment.

Note that you do not need to bother about activating virtual environments when installing or uninstalling packages using the `bin/install` and `bin/uninstall` scripts, unless you are running them directly yourself with `pip`.

```bash

# Clone the repository
$ git clone https://github.com/gr8temi/spacesAPI.git

# Change directory into the cloned folder and run the setup script
$ cd spacesAPI
$ docker compose up

# Update .env file content as necessary. Not sure if values to set? ask the Leads

```

## Running Tests

Currently, there are tests in `spaces/api/tests` folder. While always writing docker commands to run test in api container might become boring, we have a convenient script we can use to run tests within our started api container

```bash

# Ensure the api container is running in its own shell or in background
$ bin/test

```
if the above doesn't work you can run the following commands.
```bash

# Ensure the api container is running in its own shell or in background
# Open another terminal at the same root directory
# run the following commands
$ docker-compose exec api bash
$ python manage.py test

```

## Deployment

Deployment to both `staging` and `production` environments is done automatically by CircleCI after test builds passes when there is a push or merge into `develop` and `master` branches respectively.

The deployment script executed after CircleCI build is located [here](https://github.com/decagonhq/spacesAPI/blob/master/bin/deploy), which can also be run locally, but will require environment variables be properly exported in the current shell.

## License

The MIT License - Copyright (c) 2019 - Present, Decagon Institute. https://decagonhq.com/

## Notes

* Changes should be moved into both `develop` and `master` branches through merge commits so `master` always stay ahead of `develop`

