#!/bin/bash

set -x
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "$SCRIPT_DIR" >/dev/null

UnrealDir=$1
if [[ ! -e "$UnrealDir" ]]; then
    # UnrealDir variable must be set like '/Users/Shared/Epic\ Games/UE_4.16'
    echo "UnrealDir is not set."
    exit 1
fi

if [ "$(uname)" == "Darwin" ]; then
    # Call UnrealEngine shell scrpit
    pushd "$UnrealDir/Engine/Build/BatchFiles/Mac/" >/dev/null
    ./GenerateProjectFiles.sh "$SCRIPT_DIR/AirSimTest.uproject"
    popd >/dev/null
elif [ "$(uname)" == "Linux" ]; then
    # Call UnrealEngine shell scrpit
    pushd "$UnrealDir/Engine/Build/BatchFiles/Linux/" >/dev/null
    ./GenerateProjectFiles.sh "$SCRIPT_DIR/AirSimTest.uproject"
    popd >/dev/null
else

    echo "Not implemented"
    exit 1
fi

popd >/dev/null
set +x
