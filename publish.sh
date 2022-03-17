#! /bin/bash

set -e

DOCS_FOLDER="./docs"

make clean; make html
if [[ "$OSTYPE" == "linux-gnu" ]]
then
    /usr/local/opt/coreutils/libexec/gnubin/cp -rf build/html/* ${DOCS_FOLDER}/
else
    cp -rf build/html/* ${DOCS_FOLDER}/
fi 

echo "now please commit your changes and submit a PR"
