#!/bin/bash
echo "----- Now deployed web booting your repo ------ " 
gunicorn -b :5000 --reload --access-logfile - --error-logfile - dummy:app