# Hg Hooks

This documentation assumes your hg hooks are located in `~/.hg/hooks/`.

### Dependencies
* [hglib](https://www.mercurial-scm.org/wiki/PythonHglib)

TIP: To install on a mac, run `sudo easy_install python-hglib`

## Append-Jira-Commit-Message
Appends a JIRA link to the commit message.

**`.hgrc` configuration**
```
[hooks]
precommit = python:~/.hg/hooks/append_jira_commit_message.py:append_jira_commit_message

[jira]
jira.url = https://coveord.atlassian.net/browse
```

## Append-Jira-Key-Commit-Message
Appends a JIRA key to the commit message.

**`.hgrc` configuration**
```
[hooks]
precommit = python:~/.hg/hooks/append_jira_key_commit_message.py:append_jira_key_commit_message
```
