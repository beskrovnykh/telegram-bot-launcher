#!/bin/bash

setup_project() {
    local project_name="$1"
    local bot_token="$2"
    shift 2 # Remove the first two arguments

    local dependencies=""

    # If the next argument is --dependencies
    if [ "$1" == "--dependencies" ]; then
        shift # Remove --dependencies
        while [ "$#" -gt 0 ]; do
            dependencies="$dependencies $1"
            shift
        done
    fi

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    local cmd="python $DIR/../bot_project_setup.py $project_name $bot_token --dependencies $dependencies"
    eval $cmd

    # After the project directory is created, setup and activate the virtual environment
    cd $project_name
    python -m venv .venv
    source .venv/bin/activate
}

setup_project "$@"
