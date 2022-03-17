#! /bin/bash

set -e

DOCS_FOLDER="./docs"

make clean; make html

cp_command=`which cp`
if [[ "$cp_command" == "" ]]; then
  echo "$0: Failed to find the cp command"
  exit 1;
fi

$cp_command -rf build/html/* ${DOCS_FOLDER}/

echo "now please commit your changes and submit a PR"
