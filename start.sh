#!/bin/sh

cd -- "$(dirname -- "$(readlink -fn -- "$0")")"
. bin/activate
exec python neat.py
