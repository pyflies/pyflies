#!/bin/sh
# Run all tests and generate coverage report

coverage run --source pyflies -m py.test tests || exit 1
coverage report || exit 1
# coverage report --fail-under 30 || exit 1
# Run this to generate html report
# coverage html --directory=coverage
flake8 || exit 1