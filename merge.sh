#!/bin/bash

benchmarksDirectory="$1"
modelsDirectory="$2"
mergedFilesDirectory="$3"

./chcmodel/venv/bin/python3 chcmodel/merge.py "$benchmarksDirectory" "$modelsDirectory" "${mergedFilesDirectory:-mergedFiles}"
