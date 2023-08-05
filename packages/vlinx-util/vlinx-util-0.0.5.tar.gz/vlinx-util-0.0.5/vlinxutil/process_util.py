from subprocess import Popen, PIPE
from threading import Thread
import shlex


def run_process(command, show_stdout=False, show_stderr=False):
    with Popen(shlex.split(command), shell=False, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        def _stdout():
            for line in p.stdout:
                print(line, end='')

        def _stderr():
            for line in p.stderr:
                print(line, end='')

        if show_stdout:
            t = Thread(target=_stdout)
            t.start()

        if show_stderr:
            t = Thread(target=_stderr)
            t.start()

        p.wait()

        return p.returncode
