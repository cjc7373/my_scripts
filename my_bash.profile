
# some useful command
alias a=alias
a ll='ls -lh'
a log='last | grep boot | head'
a his="history | awk '{print \$2}' | sort | uniq -c | sort -k1,1nr | head -20"
a cpustat="cat /proc/cpuinfo | grep 'MHz'"
a p="pacman"
a py="python"
a grep="grep -E"

# add search path
# export PATH="$PATH:$HOME/bin:$HOME/shell"

# customize less
export LESS='-m'

export HISTSIZE=5000

