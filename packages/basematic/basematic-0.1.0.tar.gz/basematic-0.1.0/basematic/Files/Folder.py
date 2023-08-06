from jinja2 import Template
from basematic.Operate.Bash import run_cmd
import pandas as pd

def List_Folder(path):
    try:
        cmd = Template("ls -lh {{path}} | awk '{print $1, $5, $9}'").render(path = path)
        files = run_cmd(cmd)
        results = []
        for file in files:
            infos = file.split()
            try:
                if infos[0][0] == "d":
                    results.append(["folder", infos[2], ""])
                else:
                    results.append(["file", infos[2], infos[1]])
            except:
                pass
    except:
        results = []
    return pd.DataFrame(results, columns=["Type", "Name", "Size"]).sort_values(by=['Type'], ascending=False)

def deleteFolder(path):
    cmd = Template("rm -r {{path}}").render(path=path)
    files = run_cmd(cmd)
    pass

if __name__ == "__main__":
    print(List_Folder("./").to_html(index=False))