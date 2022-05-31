#!/bin/sh
find . -name migrations -exec ls {} \;

find . -name migrations -exec rm -rf {} \;
