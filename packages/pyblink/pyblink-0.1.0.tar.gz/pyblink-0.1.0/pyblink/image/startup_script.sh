#!/bin/bash

sudo apt-get update && apt-get install -y python-pip
sudo pip install numpy pandas scipy scikit-learn tensorflow xgboost
sudo shutdown -h now