import subprocess

def run_command(command, ignore_errors=False):
    r = ""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True
        )
    except Exception as e:
        if result.returncode != 0:
            error_message = f'Command "{" ".join(command)}" failed with an exception: {e}'

            if ignore_errors:
                r = result.stdout
            else:
                raise RuntimeError(error_message)
        else:
            r = result.stdout

    if result.returncode != 0:
        error_message = f'Command "{" ".join(command)}" failed (exit code {result.returncode}).\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}'

        if ignore_errors:
            r = result.stdout+"\n" + result.stderr
        else:
            raise RuntimeError(error_message)
    else:
        r = result.stdout
    return r

if __name__ == "__main__":
    # Example usage
    cmd = ["echo", "Hello, World!"]
    try:
        output = run_command(cmd)
        print("Command output:", output)
    except RuntimeError as e:
        print("Error:", e)
