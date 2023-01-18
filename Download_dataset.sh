#!/bin/sh

curl -O 
curl -O 
awk 'FNR==1 && NR!=1{next;}{print}' *.csv > master.csv