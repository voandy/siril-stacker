#!/usr/bin/env bash

ve() {
    local py=${2:-python3.10}
    local venv="${3:-./.venv}"

    local bin="${venv}/bin/activate"

	if [ -z "${VIRTUAL_ENV}" ]; then
        if [ ! -d ${venv} ]; then
            echo "Creating and activating virtual environment ${venv}"
            ${py} -m venv ${venv} --system-site-package
            echo "export PYTHON=${py}" >> ${bin}
            source ${bin}
            echo "Upgrading pip"
            ${py} -m pip install --upgrade pip
            ${py} -m pip install -r requirements.txt
            ${py} main.py "$1"
        else
            echo "Virtual environment ${venv} already exists, activating..."
            source ${bin}
            ${py} -m pip install --upgrade pip
            ${py} -m pip install -r requirements.txt
            ${py} main.py "$1"
        fi
    else
        echo "Already in a virtual environment!"
        ${py} -m pip install --upgrade pip
        ${py} -m pip install -r requirements.txt
        ${py} main.py "$1"
    fi
}

ve $@
