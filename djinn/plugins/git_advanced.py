"""
Git Advanced Plugins - Advanced Git commands.
"""


class GitPlugin:
    """Advanced Git commands."""
    
    SYSTEM_PROMPT = """You are a Git expert. Generate git commands.
Output only the command."""
    
    TEMPLATES = {
        # Basics
        "init": "git init",
        "clone": "git clone {url}",
        "clone_shallow": "git clone --depth 1 {url}",
        "status": "git status",
        "status_short": "git status -s",
        
        # Staging
        "add_all": "git add .",
        "add_file": "git add {file}",
        "add_patch": "git add -p",
        "reset_file": "git reset HEAD {file}",
        
        # Commit
        "commit": "git commit -m '{message}'",
        "commit_amend": "git commit --amend",
        "commit_amend_no_edit": "git commit --amend --no-edit",
        "commit_fixup": "git commit --fixup {commit}",
        
        # Branch
        "branch": "git branch",
        "branch_all": "git branch -a",
        "branch_create": "git checkout -b {name}",
        "branch_delete": "git branch -d {name}",
        "branch_delete_force": "git branch -D {name}",
        "branch_rename": "git branch -m {old} {new}",
        "checkout": "git checkout {branch}",
        "switch": "git switch {branch}",
        "switch_create": "git switch -c {name}",
        
        # Remote
        "remote": "git remote -v",
        "remote_add": "git remote add {name} {url}",
        "remote_remove": "git remote remove {name}",
        "fetch": "git fetch",
        "fetch_all": "git fetch --all",
        "pull": "git pull",
        "pull_rebase": "git pull --rebase",
        "push": "git push",
        "push_force": "git push --force-with-lease",
        "push_upstream": "git push -u origin {branch}",
        "push_tags": "git push --tags",
        
        # Merge/Rebase
        "merge": "git merge {branch}",
        "merge_no_ff": "git merge --no-ff {branch}",
        "merge_squash": "git merge --squash {branch}",
        "merge_abort": "git merge --abort",
        "rebase": "git rebase {branch}",
        "rebase_interactive": "git rebase -i {commit}",
        "rebase_abort": "git rebase --abort",
        "rebase_continue": "git rebase --continue",
        "cherry_pick": "git cherry-pick {commit}",
        
        # Stash
        "stash": "git stash",
        "stash_message": "git stash push -m '{message}'",
        "stash_list": "git stash list",
        "stash_pop": "git stash pop",
        "stash_apply": "git stash apply stash@{{{n}}}",
        "stash_drop": "git stash drop stash@{{{n}}}",
        "stash_clear": "git stash clear",
        
        # Log
        "log": "git log --oneline -20",
        "log_graph": "git log --oneline --graph --all",
        "log_file": "git log --follow {file}",
        "log_author": "git log --author='{author}'",
        "log_since": "git log --since='{date}'",
        "log_diff": "git log -p",
        
        # Diff
        "diff": "git diff",
        "diff_staged": "git diff --staged",
        "diff_file": "git diff {file}",
        "diff_branch": "git diff {branch1}..{branch2}",
        "diff_stat": "git diff --stat",
        
        # Reset/Revert
        "reset_soft": "git reset --soft HEAD~1",
        "reset_mixed": "git reset HEAD~1",
        "reset_hard": "git reset --hard HEAD~1",
        "reset_to_commit": "git reset --hard {commit}",
        "revert": "git revert {commit}",
        "restore": "git restore {file}",
        
        # Clean
        "clean_dry": "git clean -n",
        "clean": "git clean -fd",
        "clean_all": "git clean -fdx",
        
        # Tags
        "tag": "git tag",
        "tag_create": "git tag {name}",
        "tag_annotated": "git tag -a {name} -m '{message}'",
        "tag_delete": "git tag -d {name}",
        "tag_push": "git push origin {name}",
        
        # Blame/Bisect
        "blame": "git blame {file}",
        "bisect_start": "git bisect start",
        "bisect_good": "git bisect good",
        "bisect_bad": "git bisect bad",
        "bisect_reset": "git bisect reset",
        
        # Submodules
        "submodule_add": "git submodule add {url}",
        "submodule_update": "git submodule update --init --recursive",
        "submodule_foreach": "git submodule foreach git pull origin main",
        
        # Worktree
        "worktree_add": "git worktree add ../{name} {branch}",
        "worktree_list": "git worktree list",
        "worktree_remove": "git worktree remove {name}",
        
        # Config
        "config_list": "git config --list",
        "config_user": "git config user.name '{name}'",
        "config_email": "git config user.email '{email}'",
        "config_editor": "git config core.editor {editor}",
        
        # Maintenance
        "gc": "git gc",
        "prune": "git prune",
        "fsck": "git fsck",
        "reflog": "git reflog",
    }


class GitHubPlugin:
    """GitHub CLI commands."""
    
    TEMPLATES = {
        # Repo
        "repo_create": "gh repo create {name}",
        "repo_clone": "gh repo clone {owner}/{repo}",
        "repo_fork": "gh repo fork {owner}/{repo}",
        "repo_view": "gh repo view",
        
        # PR
        "pr_create": "gh pr create",
        "pr_create_title": "gh pr create --title '{title}' --body '{body}'",
        "pr_list": "gh pr list",
        "pr_checkout": "gh pr checkout {number}",
        "pr_merge": "gh pr merge {number}",
        "pr_view": "gh pr view {number}",
        "pr_diff": "gh pr diff {number}",
        "pr_review": "gh pr review {number} --approve",
        
        # Issues
        "issue_create": "gh issue create",
        "issue_list": "gh issue list",
        "issue_view": "gh issue view {number}",
        "issue_close": "gh issue close {number}",
        
        # Workflow
        "workflow_list": "gh workflow list",
        "workflow_run": "gh workflow run {name}",
        "workflow_view": "gh workflow view {name}",
        "run_list": "gh run list",
        "run_watch": "gh run watch {id}",
        "run_view": "gh run view {id}",
        
        # Gist
        "gist_create": "gh gist create {file}",
        "gist_list": "gh gist list",
        
        # Release
        "release_create": "gh release create {tag}",
        "release_list": "gh release list",
        "release_download": "gh release download {tag}",
        
        # Auth
        "auth_login": "gh auth login",
        "auth_status": "gh auth status",
    }


class GitLabPlugin:
    """GitLab CLI commands."""
    
    TEMPLATES = {
        "project_list": "glab project list",
        "mr_create": "glab mr create",
        "mr_list": "glab mr list",
        "mr_checkout": "glab mr checkout {number}",
        "mr_merge": "glab mr merge {number}",
        "issue_create": "glab issue create",
        "issue_list": "glab issue list",
        "ci_status": "glab ci status",
        "ci_view": "glab ci view",
    }
