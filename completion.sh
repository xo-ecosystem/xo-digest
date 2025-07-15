#!/bin/bash
_xo_fab_completions() {
  local cur_word prev_word
  cur_word="${COMP_WORDS[COMP_CWORD]}"
  prev_word="${COMP_WORDS[COMP_CWORD-1]}"
  COMPREPLY=($(compgen -W "agent0.generate-mdx agent0.start archive-all collections.ci.publish collections.core.core.validate-tasks collections.default collections.pulse.sync collections.summary collections.validate.validate collections.vault.sign-all collections.vault.verify-all cz-lint drop.generate generate-completion pulse.archive-all pulse.new pulse.sync summary sync validate-tasks vault.archive-all vault.digest-generate vault.explorer-deploy vault.publish-digest vault.render-daily vault.sign vault.sign-all vault.unlock-memethic-path vault.verify-all xo-agent.deploy-persona xo-agent.generate-mdx xo-agent.list-personas xo-agent.reload-all xo-agent.seed-personas-from-vault xo-agent.test-dialog xo.deploy-persona xo.generate-mdx xo.list-personas xo.reload-all xo.seed-personas-from-vault xo.test-dialog" -- $cur_word))
}
complete -F _xo_fab_completions xo-fab