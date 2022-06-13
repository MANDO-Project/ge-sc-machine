import re
import os
from os.path import join


def get_solc_compiler(source):
    PATTERN = re.compile(r"pragma solidity\s*(?:\^|>=|<=)?\s*(\d+\.\d+\.\d+)")
    solc_select = './sco/.solc-select/artifacts'
    solc_version = [v.split('-')[-1] for v in os.listdir(solc_select)]
    with open(join(source), encoding="utf8") as file_desc:
        buf = file_desc.read()
    version = PATTERN.findall(buf)
    version = '0.4.25' if len(version) == 0 else version[0]
    if version not in solc_version:
        if version.startswith('0.4.'):
            solc_path = join(solc_select, 'solc-' + '0.4.25')
        elif version.startswith('0.5.'):
            solc_path = join(solc_select, 'solc-' + '0.5.11')
        else:
            solc_path = join(solc_select, 'solc-' + '0.8.6')
    else:
        solc_path = join(solc_select, 'solc-' + version)
    return solc_path
