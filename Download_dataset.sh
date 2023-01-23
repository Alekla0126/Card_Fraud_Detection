#!/bin/sh

curl -O https://www.kaggle.com/datasets/kartik2112/fraud-detection/download?datasetVersionNumber=1
unzip archive.zip
mv archive Datasets
awk 'FNR==1 && NR!=1{next;}{print}' *.csv > Datasets/master.csv
rm -rf fraudTest.csv && rm -rf fraudTrain.csv