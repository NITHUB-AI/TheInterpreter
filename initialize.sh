#!/bin/bash

# pip install -r requirements.txt

git clone https://github.com/jaywalnut310/vits.git

cd vits/monotonic_align/
mkdir monotonic_align
python3 setup.py build_ext --inplace 
cd ../../
# chmod +x initialize.sh
# ./initialize.sh