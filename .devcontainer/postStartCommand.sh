#!/usr/bin/env bash

# run in the background at startup
nohup bash -c ".devcontainer/postStartBackground.sh &" > ".dev_container_logs/postStartBackground.out"

# note: do NOT have the last command run in the background else it won't really run!
