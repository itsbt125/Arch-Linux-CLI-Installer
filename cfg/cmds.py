import subprocess
from cfg.settings import VERBOSE
def cmd(command, shell=False, show_output=VERBOSE, check=True, text=False, capture_output=False, input=None):
    kwargs = {
        "shell": shell,
        "check": check,
        "text": text,
        "capture_output": capture_output,
        "input": input
    }
    if capture_output is True:
        show_output = True
    if not show_output and not capture_output:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL

    return subprocess.run(command, **kwargs)

"""
Usage examples:
cmd(["ls", "-la"], show_output=False, text=True)        # output as string, check=True
cmd(["grep", "foo", "file.txt"], check=False, text=True)
cmd("ls -la | grep py", shell=True, text=True)
cmd(["ls", "-la"], capture_output=True, text=True)      # capture stdout/stderr
"""