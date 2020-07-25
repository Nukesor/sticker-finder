#!/usr/bin/bash
host=bot@jarvis
timestamp=`date +%Y-%m-%d_%H-%m`
dest="backup/stickerfinder/stickerfinder_${timestamp}.dump"

ssh $host "mkdir -p ~/backup/stickerfinder"
ssh $host "pg_dump -F c stickerfinder > ~/$dest"
