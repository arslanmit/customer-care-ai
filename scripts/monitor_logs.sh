#!/bin/bash
# Monitor Rasa and Action server logs for errors and warnings in real time

echo "Monitoring logs for errors and warnings. Press Ctrl+C to stop."
tail -F ../logs/rasa.log ../logs/actions.log | grep --line-buffered -Ei 'error|warning'
