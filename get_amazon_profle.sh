#!/bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin
cd /home/lepython/work/venv_py3/spider
source /home/lepython/work/venv_py3/bin/activate
python /home/lepython/work/venv_py3/spider/AmazonManagerOrderCrawlFromOrderID.py
deactivate
