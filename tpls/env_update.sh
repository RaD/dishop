#!/usr/local/bin/bash

export PATH=${HOME}/env/$1/bin:${PATH}
export PYTHONPATH=${HOME}/env/$1/lib/${python_version}/site-packages
export PYTHON_EGG_CACHE=${HOME}/env/$1/.python-eggs:${PYTHON_EGG_CACHE}

pip install -E ${HOME}/env/$1 -r ${HOME}/sites/$1/deps.txt
exit 0

