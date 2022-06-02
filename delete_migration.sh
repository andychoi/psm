#!/bin/sh
find . -name migrations -exec ls {} \;

#find . -name migrations -exec rm -rf {} \;

find . -name migrations -not -path "./.venv/*" -exec rm -rf {} \;