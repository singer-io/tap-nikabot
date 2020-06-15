#!/bin/sh

set -e

PARAMS=""
while (( "$#" )); do
    case "$1" in
        --proxy)
            proxy=1
            shift 1
            ;;
        --) # end argument parsing
            shift
            break
            ;;
        *) # preserve remaining arguments
            PARAMS="$PARAMS $1"
            shift
            ;;
    esac
done
# set positional arguments in their proper place
eval set -- "$PARAMS"

source "$(dirname "$0")/.venv/Scripts/activate"
if [[ -n $proxy ]] ; then
    export HTTP_PROXY="http://localhost:8080"
    export HTTPS_PROXY="http://localhost:8080"
    export REQUESTS_CA_BUNDLE="C:\Users\paul.heasley\Documents\owasp_zap_root_ca.cer"
fi

tap-nikabot "$@"
