#!/bin/bash
# This script is run as a systemd user service at `~/.config/systemd/user/joplin-export.timer`
set -x
set -e

BACKUP_DIR="$HOME/onedrive/Notes"
BIN="joplin --log-level debug"

echo -e '\n\nBegin export'

cd $BACKUP_DIR
echo "deleting the following folders"
ls
dirs=$(ls)
if [[ -n $dirs ]] then
    ls | xargs rm -r
fi

# TODO: check syncthing status
$BIN sync
$BIN export --format md $BACKUP_DIR

echo -e '\nBegin git commit..'

git add .
git commit -m "Updated on $(date +\%Y/\%m/\%d)"
git push

echo -e 'End export\n'

