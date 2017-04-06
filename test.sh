#! /bin/bash

sudo apt-get --yes install python3.4
sudo apt-get --yes install python3-pip
sudo apt-get --yes install python-dev
sudo pip3 install virtualenv

virtualenv venv --python=python3

source venv/bin/activate
pip install -r requirements.txt
pylint asteval --output-format=parseable --rcfile pylintrc | tee pylint.out
pep8 asteval --config pep8.cfg | tee pep8.out
pytest tests/ -v --tb=short --junitxml=pytest.results.xml --cov=asteval --cov-report=term-missing --cov-report=xml

exit $?
