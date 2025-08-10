# History Scrubbing Guide

Do not run automatically. Use on a dedicated branch.

## git filter-repo

```
pipx install git-filter-repo
git filter-repo --path-glob "*.pem" --invert-paths
# example: replace a leaked token value with placeholder
git filter-repo --replace-text <(cat <<'TXT'
regex:redacted_example_token==__REDACTED__
TXT
)
```

## BFG Repo-Cleaner

```
java -jar bfg.jar --delete-files "*.pem" --delete-files "*.key" --replace-text replacements.txt
```

After scrubbing, force-push with extreme caution and coordinate with all collaborators.
