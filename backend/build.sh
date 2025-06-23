#!/bin/bash

pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
