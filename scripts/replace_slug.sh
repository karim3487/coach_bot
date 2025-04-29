#!/bin/bash

# Check if exactly one argument is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 path_to_file.py"
  exit 1
fi

FILE="$1"

# Check if the file exists
if [ ! -f "$FILE" ]; then
  echo "Error: File '$FILE' not found."
  exit 1
fi

# Perform replacement in the file
awk '
{
    if ($0 ~ /^[[:space:]]*slug:[[:space:]]*constr/) {
        sub(/slug:[[:space:]]*constr\(.*\)/, "slug: str")
    }
    print
}
' "$FILE" > "${FILE}.tmp" && mv "${FILE}.tmp" "$FILE"

echo "File '$FILE' processed successfully."
