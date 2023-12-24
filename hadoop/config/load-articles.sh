#!/bin/bash

# load articles into the hdfs dfs

# create articles directory on HDFS
hdfs dfs -mkdir -p articles

# put article files into HDFS
hdfs dfs -put ./articles/* articles

# print the an article text file for testing purposes
echo -e "\narticles article0 text_a0.txt:\n"
hdfs dfs -cat articles/article0/text_a0.txt

echo ""
