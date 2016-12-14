import re
import sys
import textwrap
import hglib


class MissingConfig(Exception):
    pass


def append_jira_commit_message(repo, **kwargs):
    commitctx = repo.commitctx
    client = hglib.open('.')

    def print_help():
        print(textwrap.dedent("""
            Append a Jira link to commit messages.

            If the current branch (or bookmark) matches the Jira project,
            and if the commit message doesn't already contain it,
            a link to the Jira is appended to commit messages.

            .hgrc configuration:
                [jira]
                jira.project = Jira project name, e.g. JIRA
                jira.url = Jira base url, e.g. https://jira.atlassian.com/browse/
            """))

    def get_config(key):
        try:
            cfg = next(cfg for cfg in client.config("jira") if cfg[1] == key)
        except (StopIteration, hglib.error.CommandError):
            raise MissingConfig("Missing configuration key '{}'".format(key))
        if not cfg:
            raise MissingConfig("Missing configuration key '{}'".format(key))
        return cfg[2]

    try:
        jira_url_base = get_config("jira.url")
    except MissingConfig as err:
        print("ERROR: {}".format(err))
        print_help()
        sys.exit(1)

    def format_message(message, jira, whence):
        jira_link = "{0}/{1}".format(jira_url_base, jira)
        if jira_link in message:
            return message
        else:
            print("\nAppended JIRA '{0}' to commit message (detected from {1}).\n".format(jira_link, whence))
            return "{0}\n\n{1}\n".format(message.strip(), jira_link)

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

    def extract_project_and_id(message):
        jira_regex = re.compile(r"^[A-Z]+-\d+")
        match = jira_regex.match(message)
        if match:
            return match.group(0)
        else:
            return None

    repo.commitctx = rewrite_ctx
