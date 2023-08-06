import os
import sys
import warnings
from os import path

def locate(name, pathenv='PATH'):
    for binpath in os.environ[pathenv].split(':'):
        if path.exists(path.join(binpath, name)):
            return path.join(binpath, name)
DEVCONFIG_FIX = ['''import devconfig
import pytest
import _pytest
import py\n''',]

def main():
    if sys.version_info.major != 2:
        return
    for scriptname in ('pytest', 'py.test'):
        pytest_script_path  = locate(scriptname)
        if pytest_script_path is not None:
            lines = []
            with open(pytest_script_path, 'r') as pytest_script:
                for line in pytest_script:
                    if len(lines) and lines[-1].startswith('# -*- coding:') and not line.startswith(DEVCONFIG_FIX[0]):
                        lines.extend(DEVCONFIG_FIX)
                    lines.append(line)
            with open(pytest_script_path, 'w') as pytest_script:
                pytest_script.write(''.join(lines))
        else:
            warnings.warn('Cant find pytest binary {!r} - pytest may be incompatible with devconfig '.format(scriptname))