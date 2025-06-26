# Bash completion for xo-fab tasks and options
_fab_completions() {
  local cur prev opts base
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  if [[ $COMP_CWORD -eq 1 ]]; then
    # Complete top-level tasks
    COMPREPLY=( $(compgen -W "$(FAB_COMPLETION=1 fab --complete)" -- "$cur") )
  elif [[ "$prev" == summary:* || "$cur" == save_to=* || "$cur" == --save_to=* || "$cur" == to_md=* || "$cur" == --to_md=* ]]; then
    COMPREPLY=( $(compgen -W "to_md=True to_md=False save_to=task_summary.md save_to=summary.md" -- "$cur") )
  fi
}
complete -F _fab_completions xo-fab