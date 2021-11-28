#!/bin/bash
BACKUP_DIR="$HOME/onedrive/Notes"
BIN="joplin --log-level debug"

echo -e '\n\nBegin export'

cd $BACKUP_DIR
find . -type f -name "*.md" -delete
rm -f _resources/*

$BIN sync
$BIN export --format md $BACKUP_DIR

echo -e '\nBegin git commit..'

git add .
git commit -m "Updated on $(date +\%Y/\%m/\%d)"

echo -e 'End export\n'

