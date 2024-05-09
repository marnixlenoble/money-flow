# Personal project


## prerequisites

- python 3.11
  - poetry 1.8.3
- node 20.10.0
  - firebase-tools 13.8.1

## getting started

run `firebase init` and when you are done run `firebase use <project name>`

create a python virtualenv `python -m venv .venv`
create a python virtualenv inside each funtion for example:

`cd functions/bunq_money_flow`
`python -m venv venv`

run `poetry install`

Now you can run the local files with `python bunq_local.py`

## deployment

make sure you are logged in to firebase, if not run `firebase login`

run `bash ./scripts/deploy.sh`
