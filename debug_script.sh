#!/bin/bash
echo "Script location debug:"
echo "BASH_SOURCE[0]: '${BASH_SOURCE[0]}'"
echo "0: '$0'"
echo "dirname BASH_SOURCE[0]: '$(dirname "${BASH_SOURCE[0]}")'"
echo "dirname 0: '$(dirname "$0")'"

if [[ -n "${BASH_SOURCE[0]}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

echo "SCRIPT_DIR: '$SCRIPT_DIR'"
