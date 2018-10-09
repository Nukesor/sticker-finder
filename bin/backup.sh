#!/usr/bin/bash
host=nuke@jarvis
timestamp=`date +%Y%m%d`
dest="backup/stickerfinder/stickerfinder_${timestamp}.dump"

ssh $host "mkdir -p ~/backup/stickerfinder"
ssh $host "pg_dump -F c stickerfinder > ~/$dest"
