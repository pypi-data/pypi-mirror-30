#!/bin/bash

# Usage:
#   source workon
#   work ...

function work()
{
    local res=$(python /Users/andre/code/github/lambert/pocs/workon/workon/workon.py "$@")
    local commands=$(echo -en "$res" | grep "EXEC:" | sed 's/EXEC://')
    # echo -en "$commands\n"
    eval "$commands"
    echo -en "$res\n" | grep -v "EXEC:"
}
