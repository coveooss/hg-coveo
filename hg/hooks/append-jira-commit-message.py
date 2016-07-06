import re,os,sys,mercurial,hglib

class MissingConfig(Exception):
    pass
 
def append_jira_commit_message(repo, **kwargs):
    commitctx = repo.commitctx
    client = hglib.open('.')
    
    def printHelp():
        print("""
Append a Jira link to commit messages.
        
If the current branch (or bookmark) matches the Jira project, 
and if the commit message doesn't already contain it,
a link to the Jira is appended to commit messages.
        
.hgrc configuration:
    [jira]
    jira.project = Jira project name, e.g. JIRA
    jira.url = Jira base url, e.g. https://jira.atlassian.com/browse/
""")
    
    def getConfig(key):
        try:
            cfg = next(cfg for cfg in client.config("jira") if cfg[1] == key)
        except (StopIteration, hglib.error.CommandError):
            raise MissingConfig("Missing configuration key '{}'".format(key))
        if not cfg:
            raise MissingConfig("Missing configuration key '{}'".format(key))
        return cfg[2]

    try:
        jiraProject = getConfig("jira.project")
        jiraUrlBase = getConfig("jira.url")
        
        # the regex is a bit lenient to allow e.g. JIRA-123_patch1
        jiraRegex = re.compile("""^{}-\d+""".format(jiraProject))
    except MissingConfig as err:
        print("ERROR: {}".format(err))
        printHelp()
        sys.exit(1)

    def format_message(str, jira, whence):
        jiraLink = "{0}/{1}".format(jiraUrlBase, jira)
        if jiraLink in str:
            return str
        else:
            print "\nAppended JIRA '{0}' to commit message (detected from {1}).\n".format(jiraLink, whence)
            return "{0}\n\n{1}\n".format(str.strip(), jiraLink)

    def rewrite_ctx(ctx, error):
        branch_name = ctx.branch()
        commitMessage = ctx._text
        match = jiraRegex.match(branch_name)
        if match:
            commitMessage = format_message(commitMessage, match.group(0), "branch name")
        else:
            bookmarks, active = client.bookmarks()
            if active != -1:
                bookmark_name = bookmarks[active][0]
                match = jiraRegex.match(branch_name)
                if match:
                    commitMessage = format_message(commitMessage, match.group(0), "bookmark name")
        
        ctx._text = commitMessage            
        return commitctx(ctx, error)
 
    repo.commitctx = rewrite_ctx
 
