#!/bin/bash

BASEDIR=$(dirname "$0")

if [[ *"zukeUI"* != $PYTHONPATH ]]; then
    export PYTHONPATH=${BASEDIR}
fi
python3 ./${BASEDIR}/ui/zukeui.py ./${BASEDIR}/assets/