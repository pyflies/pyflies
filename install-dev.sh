#!/bin/sh

pip install --upgrade pip || exit 1
pip install -e .[dev,test] || exit 1
