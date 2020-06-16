#!/bin/sh
##
# Script to execute a command within context of a .env file.
# Loads environment variables from .env before executing arguments.
# Note that environment variables passed as arguments will need to be escaped to avoid shell expansion.
#
# USAGE:
#   ./dotenv.sh my-command
#   ./dotenv.sh 'echo $MY_VAR'
##

set -e

export $(grep -v '^#' .env | xargs -0)
eval "$@"
