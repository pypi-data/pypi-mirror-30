import subprocess

def run_cmd(cmd):
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    except:
        return []
    result = [x.decode("utf-8").strip() for x in process.stdout.readlines()]
    return result
