# Welcome Bouncer REST API Backend

[![CircleCI](https://circleci.com/gh/decagonhq/bouncer-restapi/tree/master.svg?style=svg&circle-token=f84852fd9b9ee23b40fdfcf2d2e38dc5f65cb1e2)](https://circleci.com/gh/decagonhq/bouncer-restapi/tree/master)

Squad 3 - REST API backend for [Bouncer Application](https://bouncer-restapi.herokuapp.com/)

## Technolgies

* [Python 3.7](https://python.org) : Base development programming language
* [Bash Scripting](https://www.codecademy.com/learn/learn-the-command-line/modules/bash-scripting) : Create convinient script for easy development experience
* [PostgreSQL](https://www.postgresql.org/) : Application backing relational databases for both staging and production environments
* [Django Framework](https://www.djangoproject.com/) : Host development framework built on top of python
* [Django Rest Framework](https://www.django-rest-framework.org/) : Provides API development tools for easy API development
* [CircleCI]() : Continous Integration and Deployment
* [Docker Engine and Docker Compose](https://www.docker.com/) : Containerization of the appication and services orchestration

## Getting Started

Few things you need to setup to get started, set up a virtual environment majorly for isolating installs, create a `.env` file from the example file and finally install all requirements in the `requirements.txt` files within the virtual environment.

Fortunately for us, we already have a convenient [script](https://github.com/decagonhq/bouncer-restapi/blob/master/bin/setup) for this, we are only left with understanding what it actually does as opposed to just using it.

Note that you do not need to bother about activating virtual environments when installing or uninstalling packages using the `bin/install` and `bin/uninstall` scripts, unless you are running them directly yourself with `pip`.

```bash

# Clone the repository
$ git clone https://github.com/decagonhq/bouncer-restapi.git

# Change directory into the cloned folder and run the setup script
$ cd bouncer-restapi
$ bin/setup

# Update .env file content as necessary. Not sure if values to set? ask the Leads

# Start the application containers and open it in browser
$ bin/start -d && bin/open

```

## Running Tests

Currently, there is a simple truthy test in `bouncer/api/tests` folder. While always writing docker commands to run test in api container might become boring, we have a convenient script we can use to run tests within our started api container

```bash

# Ensure the api container is running in its own shell or in background
$ bin/test

```

## Deployment

Deployment to both `staging` and `production` environments is done automatically by CircleCI after test builds passes when there is a push or merge into `develop` and `master` branches respectively.

The deployment script executed after CircleCI build is located [here](https://github.com/decagonhq/bouncer-restapi/blob/master/bin/deploy), which can also be run locally, but will require environment variables be properly exported in the current shell.

## License

The MIT License - Copyright (c) 2019 - Present, Decagon Institute. https://decagonhq.com/

## Notes

* Changes should be moved into both `develop` and `master` branches through merge commits so `master` always stay ahead of `develop`

## Contributors

<table>
    <tr>
        <td align="center">
            <div>
                <img src="https://avatars2.githubusercontent.com/u/33503922?s=460&v=4" width="100px;">
                <br /><sub><b>Joel Ugwumadu</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://avatars1.githubusercontent.com/u/47976295?s=96&v=4" width="100px;">
                <br /><sub><b>Lesi Sampson</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://x1.xingassets.com/assets/frontend_minified/img/users/nobody_m.original.jpg" width="100px;">
                <br /><sub><b>Olatunde Sodiq</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://avatars3.githubusercontent.com/u/42146180?s=96&v=4" width="100px;">
                <br /><sub><b>Babalola Taiwo</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://avatars2.githubusercontent.com/u/24377769?s=460&v=4" width="100px;">
                <br /><sub><b>Ikechuku Anonymous</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://x1.xingassets.com/assets/frontend_minified/img/users/nobody_m.original.jpg" width="100px;">
                <br /><sub><b>Adams Temidire</b></sub>
            </div>
        </td>
    </tr>
    <tr>
        <td align="center">
            <div>
                <img src="https://avatars2.githubusercontent.com/u/25504617?s=96&v=4" width="100px;">
                <br /><sub><b>John Anisere - Lead</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://x1.xingassets.com/assets/frontend_minified/img/users/nobody_m.original.jpg" width="100px;">
                <br /><sub><b>Okeremeta Tega - Lead</b></sub>
            </div>
        </td>
        <td align="center">
            <div>
                <img src="https://avatars1.githubusercontent.com/u/57705536?s=96&v=4" width="100px;">
                <br /><sub><b>Abdulfatai Aka - Lead</b></sub>
            </div>
        </td>
    </tr>
</table>
