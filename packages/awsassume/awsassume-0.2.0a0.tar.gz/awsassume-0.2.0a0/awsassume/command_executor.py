import subprocess

from typing import Dict, List


class CommandExecutor(object):

    @staticmethod
    def execute(command: List[str], env_var: Dict[str, str]) -> None:
        subprocess.Popen(command, env=env_var)
