from basematic.Operate.Bash import run_cmd

def get_soft_path(name):
    return run_cmd("which "+name)