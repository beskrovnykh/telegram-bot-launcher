#!/bin/bash

run_bot() {
    local port=8080
    local stage="local"
    local venv=".venv"
    local no_autoreload=""  # by default, auto-reload is enabled
    while [[ $# -gt 0 ]]
    do
        key="$1"

        case $key in
            --stage)
            stage="$2"
            shift # past argument
            shift # past value
            ;;
            --venv)
            venv="$2"
            shift # past argument
            shift # past value
            ;;
            --no-autoreload)  # if this flag is specified, auto-reload is disabled
            no_autoreload="--no-autoreload"
            shift # past argument
            ;;
            *)    # unknown option
            shift # past argument
            ;;
        esac
    done

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    local cmd="python $DIR/../bot_launcher.py --port $port --stage $stage --venv $venv $no_autoreload"

    eval $cmd
}

run_bot "$@"