#! /bin/bash

set -e

DOCS_FOLDER="./docs"

make clean; make html
if [[ "$OSTYPE" == "linux-gnu" ]]
then
    cp -rf build/html/* ${DOCS_FOLDER}/
    rm -rf _static && mv -f ${DOCS_FOLDER}/_static .
else
    /usr/local/opt/coreutils/libexec/gnubin/cp -rf build/html/* ${DOCS_FOLDER}/
    /usr/local/opt/coreutils/libexec/gnubin/rm -rf _static && /usr/local/opt/coreutils/libexec/gnubin/mv -f ${DOCS_FOLDER}/_static .
fi 

echo "now please commit your changes and submit a PR"
