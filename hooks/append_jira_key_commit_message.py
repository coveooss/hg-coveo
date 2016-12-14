import re
import textwrap
import hglib


def append_jira_key_commit_message(repo, **kwargs):
    commitctx = repo.commitctx
    client = hglib.open('.')

    def format_message(message, jira_key, whence):
        if jira_key in message:
            return message
        else:
            print("\nAppended JIRA key '{0}' to commit message (detected from {1}).\n".format(jira_key, whence))
            return "{0} {1}".format(message.strip(), jira_key)

    def rewrite_ctx(ctx, error):
        branch_name = ctx.branch()
        commit_message = ctx._text

        found = extract_project_and_id(branch_name)
        if found:
            commit_message = format_message(commit_message, found, "branch name")
        else:
            bookmarks, active = client.bookmarks()
            if active != -1:
                bookmark_name = bookmarks[active][0]
                found = extract_project_and_id(bookmark_name)
                if found:
                    commit_message = format_message(commit_message, found, "bookmark name")

        ctx._text = commit_message
        return commitctx(ctx, error)

    repo.commitctx = rewrite_ctx


def extract_project_and_id(message):
    """Extract project name and numerical ID from a message, when it immediately starts the message or is prefixed
    by any string ended by a slash.

    Args:
        message (str): The message to match.

    Returns:
        str: The project name and ID in format NAME-ID if found, and an empty string otherwise.

    Examples:
        >>> extract_project_and_id("ABC-123-branch-name")
        'ABC-123'

        >>> extract_project_and_id("feature/ABC-123-branch-name")
        'ABC-123'

        >>> extract_project_and_id("fix/ABC-123-branch-name")
        'ABC-123'

        >>> extract_project_and_id("branch-name")
        ''

        >>> extract_project_and_id("abc-123-branch-name")
        ''

        >>> extract_project_and_id("branch-name-ABC-123")
        ''

    """
    jira_regex = re.compile(r"^(.*/)?[A-Z]+-\d+")
    match = jira_regex.match(message)
    if match:
        return match.group(0).split('/')[-1]
    else:
        return ''
