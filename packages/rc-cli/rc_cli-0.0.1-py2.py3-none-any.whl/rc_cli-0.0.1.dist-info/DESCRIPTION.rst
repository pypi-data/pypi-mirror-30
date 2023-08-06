# RoseCloud CLI
The RoseCloud CLI tool. It is intended to be used to setup and manage
a RoseCloud workspace for instructors and teaching assistants.

## Requirements
- python 3.5+

## Development
### Setup
  1. Install `pipenv`: `sudo pip install pipenv`.
  2. Run `pipenv install`.
This sets up a python virtual environment for you. All subsequent
commands should be run via `pipenv run ...`. If you need to add
another dependency, run `pipenv install <package_name>`.

### Link CLI
  1. Run `pipenv install -e .`. This will create a symlink to this
project. All changes here will show up in the `pipenv`.
  2. Run `pipenv run rc`.

**Note**: If you do not want to use `pipenv` or do not like the idea
of prefixing `pipenv run` for all commands, you can run `pipenv`
with `pip install -e .`


