#!/bin/bash
# LLM Response Cache Script
# Caches LLM responses to reduce API calls

CACHE_DIR="/tmp/llm_cache"
mkdir -p "$CACHE_DIR"

hash_prompt() {
    echo -n "$1" | sha256sum | cut -d' ' -f1 | cut -c1-16
}

get_cached() {
    prompt="$1"
    max_age="${2:-3600}"  # default 1 hour
    
    key=$(hash_prompt "$prompt")
    cache_file="$CACHE_DIR/$key.json"
    
    if [ -f "$cache_file" ]; then
        age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0)))
        if [ "$age" -lt "$max_age" ]; then
            cat "$cache_file"
            return 0
        fi
    fi
    return 1
}

save_cached() {
    prompt="$1"
    response="$2"
    key=$(hash_prompt "$prompt")
    cache_file="$CACHE_DIR/$key.json"
    
    echo "$response" | jq -Rs '.' > "$cache_file"
}

clear_cache() {
    rm -rf "$CACHE_DIR"/*
    echo "Cache cleared"
}

case "$1" in
    "get")
        get_cached "$2" "${3:-3600}"
        ;;
    "save")
        save_cached "$2" "$3"
        ;;
    "clear")
        clear_cache
        ;;
    *)
        echo "Usage: llm-cache.sh [get|save|clear] [prompt] [response]"
        ;;
esac
