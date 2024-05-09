#!/bin/bash


declare -A basePaths=(["bunq"]="functions/bunq_money_flow")
declare -A extraDependencies=(["bunq"]="--with bunq")
declare -A extraScripts=(["bunq"]="scripts/bunq_deploy.sh")
declare -A functionNames=(["bunq"]="bunq_monthly_sorter")
firebaseFunctions=""

if [ $# -eq 0 ]; then
    args=("bunq")
else
    args=("$@")
fi

for function in "$args"; do
    path=${basePaths[$function]}
    extraScript=${extraScripts[$function]}
    functionName=${functionNames[$function]}

    [ -z "$path" ] && echo "$function is not a valid options. Valid options are: ${!basePaths[@]}" && exit 1

    if [ -n "$extraScript" ]; then
        bash "$extraScript"
    fi

    rm -rf "$path"/lib/
    cp -a lib/. "$path"/lib/

    poetry export -f requirements.txt --output "$path"/requirements.txt ${extraDependencies[$function]} --without-hashes

    cd "$path"
    source "./venv/bin/activate"
    pip install -r requirements.txt
    deactivate
    cd ../..

    firebaseFunctions+="functions:$functionName,"
done 

firebase deploy --only firestore,${firebaseFunctions::-1}
