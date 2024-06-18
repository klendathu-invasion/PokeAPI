#!/bin/bash
if ! pip freeze | diff requirements.txt -;
then
    echo -e "\n\nYou need to update requirements for the app works on docker."
    echo -e "\e[1;33mRun the command :"
    echo -e "\t\e[0;31mpip freeze > requirements.txt\e[0m"
    exit 1
fi
