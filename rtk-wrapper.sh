#!/bin/bash
# RTK Wrapper - Reduce Token Usage for Common Commands
# Wraps commands with token-efficient output

COMMAND="$1"
shift

case "$COMMAND" in
    "ls")
        ls -la "$@" | head -20
        ;;
    "cat")
        head -50 "$1"
        ;;
    "git")
        git "$@" | head -30
        ;;
    "grep")
        grep "$@" | head -20
        ;;
    "ps")
        ps aux | head -15
        ;;
    "df")
        df -h | grep -v tmpfs
        ;;
    "free")
        free -h
        ;;
    "ss")
        ss -tlnp | head -20
        ;;
    *)
        echo "RTK: Unknown command: $COMMAND"
        echo "Usage: rtk <command>"
        ;;
esac
