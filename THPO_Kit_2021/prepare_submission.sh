#!/bin/bash

# get searcher directory
INPUT_DIR=$1

# directory of searcher 
CODE_DIR=$(dirname $INPUT_DIR)/$(basename $INPUT_DIR)
echo $CODE_DIR

# check if not implement searcher.py
if [ ! -f "$CODE_DIR/searcher.py" ]; then
    echo "Please implemente searcher.py in "$CODE_DIR
    exit 0
fi

# upload directory
UPLOAD_DIR=upload_$(basename $INPUT_DIR)_$(date "+%m%d%H%M")
echo $UPLOAD_DIR

cp -r -n $CODE_DIR ./$UPLOAD_DIR

# touch requirements.txt
REQUIREMENTS_FILE=./$UPLOAD_DIR/requirements.txt
touch $REQUIREMENTS_FILE

# download extra package in requirements.txt
pip3 download -r $REQUIREMENTS_FILE -d ./$UPLOAD_DIR --python-version 36 --implementation cp --platform linux_x86_64 --abi cp36m --no-deps

! test -f $UPLOAD_DIR.zip

# delete pycache
rm -rf ./$UPLOAD_DIR/__pycache__

(cd $UPLOAD_DIR && zip -r ../$UPLOAD_DIR.zip ./*)

echo "----------------------------------------------------------------"
echo "Built achive for upload"
unzip -l ./$UPLOAD_DIR.zip

echo "For scoring, upload $UPLOAD_DIR.zip at address:"
echo "https://algo.browser.qq.com/"
