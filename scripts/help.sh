#!/bin/bash

# =========================================================
# Customer Care AI - Script Help
# Lists and describes all available scripts
# =========================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

list_scripts() {
    echo -e "\n${GREEN}Available scripts:${NC}"
    echo -e "\n${YELLOW}Development:${NC}"
    for f in dev/*.sh; do
        [ -e "$f" ] || continue
        echo "  scripts/$f - $(head -5 $f | grep -v '^#\|^$' | head -1 | sed 's/# //')"
    done
    echo -e "\n${YELLOW}Deployment:${NC}"
    for f in deployment/*.sh deployment/*/*.sh; do
        [ -e "$f" ] || continue
        echo "  scripts/$f - $(head -5 $f | grep -v '^#\|^$' | head -1 | sed 's/# //')"
    done
    echo -e "\n${YELLOW}Utilities:${NC}"
    for f in utils/*.sh; do
        [ -e "$f" ] || continue
        echo "  scripts/$f - $(head -5 $f | grep -v '^#\|^$' | head -1 | sed 's/# //')"
    done
}

list_scripts
