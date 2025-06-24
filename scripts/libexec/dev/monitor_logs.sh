
show_help() {
    echo "Usage: ./monitor_logs.sh [options]"
    echo "  -h, --help   Show this help message and exit"
}

for arg in "$@"; do
    case $arg in
        -h|--help)
            show_help
            exit 0
            ;;
    esac
done

#!/bin/bash
# Usage: ./scripts/dev/monitor_logs.sh [options]
# Run with -h or --help for usage information
# Monitor Rasa and Action server logs for errors and warnings in real time

echo "Monitoring logs for errors and warnings. Press Ctrl+C to stop."
tail -F ../logs/rasa.log ../logs/actions.log | grep --line-buffered -Ei 'error|warning'
