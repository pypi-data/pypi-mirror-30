from subprocess import Popen, PIPE
from threading import Thread
import shlex


def run_process(command, show_stdout=True, show_stderr=True):
    with Popen(shlex.split(command), shell=False, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        def show_stdout():
            for line in p.stdout:
                print(line, end='')

        def show_stderr():
            for line in p.stderr:
                print(line, end='')

        if show_stdout:
            t = Thread(target=show_stdout)
            t.start()

        if show_stderr:
            t = Thread(target=show_stderr)
            t.start()

        p.wait()

        return p.returncode
