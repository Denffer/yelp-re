#!/bin/zsh

for i in data/reviews/*.json
do 
    ts -n -f sh -c "python ReviewParser.py $i" &
done
ts -S 10

