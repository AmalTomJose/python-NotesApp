#!/bin/bash

echo "adding file"
git add .
echo "enter commit message"
read message
echo "commiting file"
git commit -m "$message"
echo "pushing file"
git push origin main
echo  "done!"
