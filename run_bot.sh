#!/bin/bash

run_bot() {
    local port=8080
    local stage="local"
    local venv=".venv"
    local no_autoreload=""  # по умолчанию автоперезагрузка включена

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
            --no-autoreload)  # если данный флаг указан, автоперезагрузка отключается
            no_autoreload="--no-autoreload"
            shift # past argument
            ;;
            *)    # unknown option
            shift # past argument
            ;;
        esac
    done

    local cmd="bot_launcher.py --port $port --stage $stage --venv $venv $no_autoreload"
    eval $cmd
}

run_bot "$@"