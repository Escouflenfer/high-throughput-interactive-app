#!/bin/sh

python -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

mkdir ./data
mkdir ./data/EDX ./data/MOKE ./data/XRD
mkdir ./results
mkdir ./results/EDX ./results/MOKE ./results/XRD