[TOC]

# Hg Hooks

This documentation assumes your hg hooks are located in `~/.hg/hooks/`.

### Dependencies
* [hglib](https://www.mercurial-scm.org/wiki/PythonHglib)

TIP: To install on a mac, run `sudo easy_install python-hglib`

## Append-Jira-Commit-Message
**`.hgrc` configuration**
```
[hooks]
precommit = python:~/.hg/hooks/append-jira-commit-message.py:append_jira_commit_message

[jira]
jira.project = MYJIRAPROJECT
jira.url = https://myjira.atlassian.net/browse
```
