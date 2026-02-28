import subprocess
from cfg import settings

def cmd(command, shell=False, show_output=None, check=True, text=True, capture_output=False, input=None):
    # default show_output to settings.VERBOSE
    if show_output is None:
        show_output = settings.VERBOSE

    # if we want to show output, capture it so we can print
    if show_output is True and capture_output is False:
        capture_output = True

    kwargs = {
        "shell": shell,
        "check": check,
        "text": text,
        "capture_output": capture_output,
        "input": input
    }

    # suppress output if neither show_output nor capture_output
    if not show_output and not capture_output:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL

    result = subprocess.run(command, **kwargs)

    # print output if verbose
    if show_output:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")

    return result
"""
Usage examples:
cmd(["ls", "-la"], show_output=False, text=True)        # output as string, check=True
cmd(["grep", "foo", "file.txt"], check=False, text=True)
cmd("ls -la | grep py", shell=True, text=True)
cmd(["ls", "-la"], capture_output=True, text=True)      # capture stdout/stderr
"""