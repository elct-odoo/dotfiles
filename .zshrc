# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# If you come from bash you might have to change your $PATH.
#export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH=$HOME/.oh-my-zsh

export PATH=/bin/lscript:/bin/lscript:/home/sarthak/anaconda3/bin:/home/sarthak/anaconda3/condabin:/home/sarthak/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
PATH=$PATH:~/.local/bin
export PATH=$PATH:/home/sarthak/Desktop/go/commit
export PATH=$PATH:/usr/local/go/bin

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/sarthak/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/sarthak/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/home/sarthak/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/sarthak/anaconda3/bin:$PATH"
    fi
fi
# >>>>>>>>>>>>>>>>>>>

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes


ZSH_THEME="powerlevel10k/powerlevel10k"

POWERLEVEL9K_MODE="nerdfont-complete"
POWERLEVEL9K_DISABLE_RPROMPT=true
POWERLEVEL9K_PROMPT_ON_NEWLINE=true
POWERLEVEL9K_MULTILINE_LAST_PROMPT_PREFIX="▶" 
POWERLEVEL9K_MULTILINE_FIRST_PROMPT_PREFIX=""



# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
# DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS=true

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.

# PLUGINS HERE
plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-history-substring-search)


source $ZSH/oh-my-zsh.sh

# alias entries
alias lc='colorls'
alias newdb='sh /home/odoo/dev/support/us-support/scripts/generic/newdb'
alias download-custom='echo "tar -czvf archive.tar.gz ." | xclip -selection clipboard'
alias shitshow='source ~/.venvs/shitshow/bin/activate'

# oes shit
path_to_python="/usr/bin/python3"
path_to_support_tools="/home/odoo/dev/support/support-tools"
oe-support() {
	$path_to_python $path_to_support_tools/oe-support.py $@
}

oes() {
	$path_to_python $path_to_support_tools/oe-support.py $@
}

#clean_database() {
#	$path_to_python $path_to_support_tools/clean_database.py $@
#}

# Activate bash style completion
# If you use oh-my-zsh, bashcompinit should already be autoloaded
autoload bashcompinit
bashcompinit
source /home/odoo/dev/support/support-tools/scripts/completion/oe-support-completion.sh
complete -o default -F _oe-support oes
source /home/odoo/dev/support/support-tools/scripts/completion
complete -o default -F _clean-database clean_database


# Search for "dblink" in a SQL dump with optional context length
dblinkgrep() {
  # first param error handling
  if [[ -z "$1" ]]; then
    echo "Usage: dblinkgrep <dump.sql> [context_length]"
    return 1
  fi

  local file="$1"
  local context="${2:-30}"  # Default to 30 if not provided
  
  # verify the file is valid if given
  if [[ ! -f "$file" ]]; then
    echo "File not found: $file"
    return 1
  fi

  # assign number of bytes (chars)
  local size=$(wc -c < "$file" | tr -d '[:space:]')
  
  # Stream the file with a progress bar (using known size), then search case-insensitively for 'dblink'
# Output only matched snippets showing up to $context characters before and after each occurrence
  pv -p -s "$size" "$file" | grep -i -o -E ".{0,${context}}dblink.{0,${context}}"
}


#func for scp
copy() {
    local user_and_host="$1"
    local remote_path="~/src/user"
    local destination_path="$HOME/dev/src"
    scp -r "$user_and_host:$remote_path" "$destination_path"
}

# User configuration
export GOPATH=~/go

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
   export EDITOR='vim'
 else
   export EDITOR='mvim'
fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

export LANG=en_US.UTF-8

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# To customize prompt, run `p10k configure` or edit ~/p10k.zsh.
[[ ! -f ~/p10k.zsh ]] || source ~/p10k.zsh
