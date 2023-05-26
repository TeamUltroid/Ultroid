import os
from subprocess import run, PIPE

class InvalidGitPath(Exception):
    ...

class GitError(Exception):
    ...

class Repo:
    def __init__(self, path: str = ".") -> None:
        self._path = path
    
    def active_branch(self):
        return self._run("git rev-parse --abbrev-ref HEAD").strip()

    def remotes(self):
        return [remote.strip() for remote in self._run("git remote").split("\n") if remote]
    
    def fetch_remote(self, remote: str = "origin"):
        return self._run(["git", "fetch", remote])

    def get_remote_url(self, remote: str="origin"):
        return self._run(f"git remote get-url {remote}")

    def rev_parse(self, remote: str = "origin"):
        return self._run(["git", "rev-parse", remote])

    def _run(self, cmd):
        if not os.path.exists(f"{self._path}/.git"):
            raise InvalidGitPath("No git repository initialised on given path.")
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        proc = run(cmd, cwd=self._path, stdout=PIPE, stderr=PIPE)
        if proc.stderr and proc.returncode:
            raise GitError(f"Command exited with error: {proc.stderr}, output: {proc.stdout}")
        out = proc.stdout or proc.stderr 
        if out is None:
            raise GitError('Unknown Error: command output not found')
        return out.decode()

repo = Repo()