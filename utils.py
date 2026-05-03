import requests
import json
import os
import glob
import time
import sys
import re
import signal
import argparse
import subprocess
from subprocess import TimeoutExpired
from static_check.codeChecker import check_rank_consistency
from static_check.rankingChecker import validate_c_file
from static_check.astChecker import *
from utils import *
from prompt import *
import clang
from clang.cindex import Index, CursorKind
def save_dict_to_txt(data_dict, filename):

    try:
        with open(filename, 'w', encoding='utf-8') as f:

            f.write("name\tresult\tin_tokens\tout_tokens\ttime_used\n")
            f.write("-" * 30 + "\n")
            
            for name, result in data_dict.items():
                f.write(f"{name}\t{result}\n")
        
        print(f"save result: {filename}")
        return True
    except Exception as e:
        print(f"save result failed: {e}")
        return False
def RunClangCommand(file_name):
    # Command line
    #os.system("rm -f tmp.o && rm -f " + SPEC_FILE)
    VERI_CLANG_Command = ["veri-clang", "-O0", "-c", file_name, "-o", "tmp.o"]

    # create subprocess according to the value of check_STDOUT and check_STDERR
    process = subprocess.Popen(VERI_CLANG_Command, close_fds=True, preexec_fn=os.setpgrp)
    process.communicate()
def TransformDict(SpecLocList):
    SpecDictList = []
    for SpecLoc in SpecLocList:
        SpecDict = {}
        func_name, func_loc, loop_loc = SpecLoc.split('===')
        SpecDict['func_name'] = func_name
        
        if ":" in func_loc:
            file_name, func_loc = func_loc.rsplit(':')
            SpecDict['file_name'] = file_name
            SpecDict['func_loc'] = int(func_loc)
        else:
            print("func_loc error")
            sys.exit(2)

        if loop_loc == '0':
            SpecDict['loop_loc'] = []
        elif ',' in loop_loc:
            loop_loc = loop_loc.split(',')
            #SpecDict['loop_loc'] = list(map(int, loop_loc)) # Convert all strings in a list to integers
            SpecDict['loop_loc'] = list(loop_loc)
        elif loop_loc.replace('@', '').isdigit():
            #SpecDict['loop_loc'] = [int(loop_loc)]
            SpecDict['loop_loc'] = [loop_loc]
        else:
            print(loop_loc)
            print("loop_loc does not exist")
        SpecDictList.append(SpecDict)
    return SpecDictList
def FindLoopLine(file_name,SpecDictList):
    _tList = []
    with open(file_name, "r") as f:
        file_open = f.read()
    for _tDict in SpecDictList:
        for _tDictValue in _tDict["loop_loc"]:
            _tDictValue = _tDictValue.replace("@","")
            _tDictValue = int(_tDictValue)
            lines_cnt = 0
            for lines in file_open.splitlines():
                lines_cnt += 1
                if lines_cnt ==  _tDictValue:
                    _tList.append(lines)
    return _tList
def save_string_to_file(text, filename="./output.txt"):

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text + '\n')  
        
        print(f"save result: {filename}")
        return True
    
    except Exception as e:
        print(f"save result failed: {str(e)}")
        return False
def extract_counterexample(text):

    lines = text.splitlines()
    result_lines = []
    in_failure_path = False

    for line in lines:
        if line.startswith("  - CounterExampleResult"):
            in_failure_path = True
            result_lines.append(line)  
            continue

        if in_failure_path:
            if line.startswith("  - "):
                break
            result_lines.append(line)

    return "\n".join(result_lines) if result_lines else ""

