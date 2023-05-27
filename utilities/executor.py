import contextlib, subprocess


class Terminal:
    """
    Class for running terminal commands asynchronously.

    Methods:

        run(commands: str)
            commands: Terminal Commands.
            Returns Process id (int)

        terminate(pid: int)
            pid: Process id returned in `run` method.
            Returns True if terminated else False (bool)

        output(pid: int)
            pid: Process id returned in `run` method.
            Returns Output of process (str)

        error(pid: int)
            pid: Process id returned in `run` method.
            Returns Error of process (str)
    """

    def __init__(self) -> None:
        self._processes = {}

    @staticmethod
    def _to_str(data: bytes) -> str:
        return data.decode("utf-8").strip()

    async def run(self, *args) -> int:
        process = subprocess.Popen(
            *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        pid = process.pid
        self._processes[pid] = process
        return pid

    def terminate(self, pid: int) -> bool:
        try:
            self._processes[pid].kill()
            self._processes.pop(pid)
            return True
        except KeyError:
            return False
    
    def _readline(self, pid:int, stdout=False) -> str:
        output = []
        attr = getattr(self._processes[pid], "stdout" if stdout else "stderr")
        while True:
            if out := self._to_str(attr.readline()):
                output.append(out)
                continue
            break
        return "\n".join(output)
    
    def error(self, pid: int) -> str:
        return self._readline(pid)

    def output(self, pid: int) -> str:
        return self._readline(pid, True)

    @property
    def _auto_remove_processes(self) -> None:
        while self._processes:
            for proc in self._processes.keys():
                if proc.returncode is not None:  # process is still running
                    with contextlib.suppress(KeyError):
                        self._processes.pop(proc)
