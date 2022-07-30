#!/bin/bash

outputDirectory="$1"
modelsDirectory="$2"

./chcmodel/venv/bin/python3 chcmodel/convert.py "$outputDirectory" "${modelsDirectory:-models}"