#!/usr/bin/env bash
# =========================================================
# Script: help.sh
# Description: Lists and describes all available scripts in the bin directory
# =========================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${SCRIPT_DIR}/bin"

# Print header
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Customer Care AI - Available Scripts${NC}"
    echo -e "${BLUE}================================================${NC}"
}

# Print a section header
print_section() {
    echo -e "\n${YELLOW}$1${NC}"
    echo "$(printf '%.0s-' {1..50})"
}

# Get script description
get_script_description() {
    local script_path="$1"
    local description=""
    
    # Try to get description from script
    if [ -f "$script_path" ]; then
        description=$(grep -m 1 -E '^# Description:' "$script_path" 2>/dev/null | sed 's/^# Description: //')
    fi
    
    echo "$description"
}

# Categorize scripts
categorize_scripts() {
    local -n categories=$1
    
    # Initialize categories
    categories[development]=""
    categories[deployment]=""
    categories[setup]=""
    categories[utils]=""
    categories[other]=""
    
    # Find all symlinks in bin directory
    while IFS= read -r -d '' script; do
        # Skip directories and non-symlinks
        [ -L "$script" ] || continue
        
        # Get the target of the symlink
        local target_path=$(readlink "$script")
        local script_name=$(basename "$script")
        
        # Get the full path to the actual script
        local full_script_path="${BIN_DIR%/*}/$target_path"
        local description=$(get_script_description "$full_script_path")
        
        # Categorize based on the target path
        if [[ "$target_path" == *"/dev/"* ]]; then
            categories[development]+="$script_name|$description\n"
        elif [[ "$target_path" == *"/deployment/"* ]]; then
            categories[deployment]+="$script_name|$description\n"
        elif [[ "$target_path" == *"/setup/"* ]]; then
            categories[setup]+="$script_name|$description\n"
        elif [[ "$target_path" == *"/utils/"* ]]; then
            categories[utils]+="$script_name|$description\n"
        else
            categories[other]+="$script_name|$description\n"
        fi
    done < <(find "$BIN_DIR" -type l -print0 2>/dev/null | sort -z)
}

# Print a category of scripts
print_category() {
    local title="$1"
    local items="$2"
    local count=0
    
    echo -e "\n${GREEN}${title}:${NC}"
    echo "$(printf '%.0s-' $(seq 1 $((${#title} + 1))))"
    
    # Process each item in the category
    while IFS= read -r item; do
        [ -z "$item" ] && continue
        local script_name=$(echo "$item" | cut -d'|' -f1)
        local description=$(echo "$item" | cut -d'|' -f2-)
        
        printf "  %-25s %s\n" "./bin/$script_name" "$description"
        ((count++))
    done < <(echo -e "$items" | sort)
    
    if [ $count -eq 0 ]; then
        echo "  No scripts found"
    fi
}

# Main function
main() {
    print_header
    
    # Categorize all scripts
    declare -A categories
    categorize_scripts categories
    
    # Print each category
    print_category "Development Scripts" "${categories[development]}"
    print_category "Deployment Scripts" "${categories[deployment]}"
    print_category "Setup Scripts" "${categories[setup]}"
    print_category "Utility Scripts" "${categories[utils]}"
    
    # Print other scripts if any
    if [ -n "${categories[other]}" ]; then
        print_category "Other Scripts" "${categories[other]}"
    fi
    
    echo -e "\n${BLUE}Usage:${NC} Run any script with --help for more information"
    echo -e "${BLUE}Documentation:${NC} See scripts/README.md for more details"
}

# Run the main function
main "$@"
