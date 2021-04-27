#!/bin/sh

#trap 'echo sigterm trapped' SIGTERM
trap 'echo sigint trapped' SIGINT
#trap 'echo sigkill trapped' SIGKILL
sleep 100
echo Done
