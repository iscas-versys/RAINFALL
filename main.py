#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import os
import glob
import time
import sys
import re
import signal
import json
import argparse
import subprocess
from subprocess import TimeoutExpired
from static_check.codeChecker import check_rank_consistency
from static_check.rankingChecker import validate_c_file
from static_check.astChecker import check_AST
from utils import *
from prompt import *
import clang
from clang.cindex import Index, CursorKind
api_key = ""

SPEC_FILE = "SpecLoC.txt"
llm_model = ""
data_path = ""
result_path = ""
platform = ""
url = ""


def GetSpecLoc():
    if os.path.exists(SPEC_FILE):
        with open(SPEC_FILE, 'r') as f:
            lines = f.readlines()
            SpecLocList = []
            for line in lines:
                line = line.strip('\n')
                SpecLocList.append(line)
            return SpecLocList
    else:
        print("Error: SpecLoC.txt does not exist")
        sys.exit(2)

def analyze_with_llm(iterate_prompt, max_tokens = 5000):
    """
    Query the LLM using a prompt that contains counterexample information.
    
    Args:
        counter_prompt (str): Prompt containing counterexample details.
        
    Returns:
        str: LLM response content, or None if an error occurs.
    """

    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {}
    print(platform)
    if platform == "deepseek":
        payload = {
            "model": llm_model,
            "messages": [{"role": "user", "content": iterate_prompt}],
            "temperature": 0.0,  
        }
    if platform == "openrouter":
        payload = {
            "model": llm_model,
            "reasoning": {"enabled": True},
            "messages": [{"role": "user", "content": iterate_prompt}],
            "temperature": 0.0,  
        }
    if platform == "aliyun":
        payload = {
            "model": llm_model,
            "reasoning": {"enabled": True},
            "messages": [{"role": "user", "content": iterate_prompt}],
            "temperature": 0.2,  
            "enable_thinking":True
        }
    try:
        start_time = time.time()  
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload),  
            timeout=300 
        )
        end_time = time.time()  
        call_time = end_time - start_time  
        if response.status_code == 200:
            
            response_data = response.json()
            if 'usage' in response_data:
                usage = response_data['usage']
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
            

            return response_data['choices'][0]['message']['content'], input_tokens, output_tokens, call_time
        else:
            print(f"API error: status code {response.status_code}")
            print(f"Error details: {response.text}")
            return None,0,0,0.0
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None,0,0,0.0
    except (KeyError, IndexError) as e:
        print(f"Failed to parse response: {str(e)}")
        print("Raw response:", response.text)
        return None,0,0,0.0
    except json.JSONDecodeError:
        print("JSON parsing failed")
        print("Raw response:", response.text)
        return None,0,0,0.0

def call_llm_with_retry(prompt, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        content, in_tok, out_tok, used_time = analyze_with_llm(prompt, **kwargs)
        if content is not None:
            return content, in_tok, out_tok, used_time
        print(f"LLM call failed (attempt {attempt+1}/{max_retries}), waiting and retrying...")
        time.sleep(2 ** attempt)  
    print("Max retries exhausted, abandoning this call")
    return None, 0, 0, 0.0   

def process_c_files(folder_path, llm_max, counter_max,output_dir="termination_results", ultimate_dir='/workspace/UltimateAutomizer-linux/UAutomizer-linux'):
    """
    Process all C files in a folder and save analysis results.
    """
    os.makedirs(output_dir, exist_ok=True)
    c_files = glob.glob(os.path.join(folder_path, "*.c"))
    if not c_files:
        print(f"No C files found in {folder_path}")
        return
    
    print(f"Found {len(c_files)} C files. Starting analysis...")
    result = ""
    result_dict = {}
    true_cnt = 0
    for i, file_path in enumerate(c_files):
        file_name = os.path.basename(file_path)
        result_dict.setdefault(file_name, "FALSE")
        print(f"Analysis completed for {i} files. {true_cnt} programs proved to terminate.")
        print(f"Processing ({i+1}/{len(c_files)}): {file_name}")
        final_result = "FALSE"
        total_input_tokens = 0
        total_output_tokens = 0
        total_analysis_time = 0.0
        RunClangCommand(file_path)
        # get SpecLoC
        SpecLocList = GetSpecLoc()
        # Transform SpecLoC to SpecDict
        SpecDictList = TransformDict(SpecLocList)
        _TAG = 0
        _tLoopList = FindLoopLine(data_path + "/" + file_name,SpecDictList)
        print("Analyzing loops:", _tLoopList)
        for _tLoop in _tLoopList:
            analyze_finish = 0
            llm_stage = 0
            while llm_stage < llm_max:
                if analyze_finish == 1:
                    break
                llm_stage = llm_stage + 1

                print(f"LLM analysis round {llm_stage} started...")
                generate_code_Infill(file_name,_tLoop,_TAG)
                with open(result_path + "/" + file_name, "r") as f:
                    c_code = f.read()
                _tccode = c_code
                result = ""
                initial_prompt = generate_c_termination_initial(c_code,file_name)
                result, in_tok, out_tok, t_used = call_llm_with_retry(initial_prompt)
                log_llm_interaction(file_name, initial_prompt, result)  
                total_input_tokens += in_tok
                total_output_tokens += out_tok
                total_analysis_time += t_used

                if result == None:
                    result = ""
                print("LLM feedback received, waiting for Ultimate verification...")
                result = result.replace("```c","")
                result = result.replace("```","")
                print(result)
                j = 0
                jmax = counter_max+1
                save_string_to_file(result +"\n",result_path + "/" + file_name)
                #print("result:",result)
                while j < jmax:
                    if result == "":
                        result_dict[file_name]=result_dict[file_name] +"_LLM_FALSE"+str(j)+" "
                        break

                    if j > 1:
                        print(f"Analysis attempt {j-1}:")
                   # -------------------------------- AST CHECK --------------------------------
                    print("check_AST start.")
                    while True:
                        _bAST,msg = check_AST(file_path,result_path + "/" + file_name)

                        if _bAST == False:
                            result_dict[file_name] = result_dict[file_name] + "_AST_FALSE"+str(j)+" "
                            j = j+1
                            if j >= jmax:
                                break
                            print("AST check FALSE!")
                            _ASTPrompt = generate_ASTERROR_prompt(_tccode,result, msg)
                            result, in_tok, out_tok, t_used = call_llm_with_retry(_ASTPrompt)
                            log_llm_interaction(file_name, _ASTPrompt, result)   # Record log
                            total_input_tokens += in_tok
                            total_output_tokens += out_tok
                            total_analysis_time += t_used
                            if result == None:
                                result = ""
                                break
                            print("LLM feedback received, waiting for Ultimate verification...")
                            result = result.replace("```c","")
                            result = result.replace("```","")
                            save_string_to_file(result +"\n",result_path + "/" + file_name)
                        else:
                            print("AST check OK!")
                            break
                    if _bAST == False:
                            break
                   # -------------------------------- CODE CHECK --------------------------------
                    while True:
                        codeStatus,rank_inf = check_rank_consistency(result)
                        if codeStatus == 6 or codeStatus == 5:
                            result_dict[file_name]=result_dict[file_name] +"_LLM_FALSE"+str(j)+" "
                            break
                        print("rank_inf:", rank_inf)

                        print("codeStatus:",codeStatus)
                        if codeStatus != 1:
                            result_dict[file_name] = result_dict[file_name] + "_code_FALSE"+str(j)+" "
                            j = j+1
                            if j >= jmax:
                                break
                            if 'errors' in rank_inf:
                                combined_str = '\n'.join(rank_inf['errors'])
                                
                            else:
                                combined_str = rank_inf["inf"]  
                            _codePrompt = generate_code_prompt(_tccode,result,error_information_dict[codeStatus],combined_str)
                            result, in_tok, out_tok, t_used = call_llm_with_retry(_codePrompt)
                            log_llm_interaction(file_name, _codePrompt, result)   # Record log
                            if result == None:
                                result = ""
                                break
                            total_input_tokens += in_tok
                            total_output_tokens += out_tok
                            total_analysis_time += t_used
                            print("code check FALSE!")
                            
                        else:
                            print("code check OK!")
                            break
                    if codeStatus != 1:
                        break
                   # -------------------------------- ASSERT CHECK --------------------------------
                    bool_CheckRanking, RankingStr = validate_c_file(result)
                    if bool_CheckRanking == False:
                        print("check Ranking fucntion False!")
                        result_dict[file_name] = result_dict[file_name] + "_ASSERT_FALSE"+str(j)+" "
                        while True:
                            j = j+1
                            if j >= jmax:
                                break
                            _RankingFucntionPrompt = generate_RankingFucntion_prompt(_tccode,result,RankingStr)
                            result, in_tok, out_tok, t_used = call_llm_with_retry(_RankingFucntionPrompt)
                            log_llm_interaction(file_name, _RankingFucntionPrompt, result)   # Record log
                            total_input_tokens += in_tok
                            total_output_tokens += out_tok
                            total_analysis_time += t_used
                            if result == None:
                                result = ""
                            print("LLM feedback received, waiting for Ultimate verification...")
                            result = result.replace("```c","")
                            result = result.replace("```","")
                            bool_CheckRanking, RankingStr = validate_c_file(result)
                            if bool_CheckRanking == False:
                                print("check Ranking fucntion still False!")
                                continue
                            else:
                                print("check Ranking fucntion OK!")
                                break
                        
                    else:
                        print("check Ranking fucntion OK!")
                    if bool_CheckRanking == False:
                        break
                    result = result.replace("```c","")
                    result = result.replace("```","")
                    save_string_to_file(result +"\n",result_path + "/" + file_name)
                    save_string_to_file(result +"\n",result_path + "/" + file_name.replace(".c","_"+str(j)+"_.c"))
                   # -------------------------------- UAutomizer CHECK --------------------------------
                    ultimate_result,ultimate_time  = run_termination_command(result_path + "/" + file_name,file_name.replace(".c",""),ultimate_dir)
                    total_analysis_time += ultimate_time   
                    if ultimate_result == False:
                        import subprocess
                        subprocess.run(["pkill", "z3"])
                        result_dict[file_name]=result_dict[file_name] +"_TIMELIMIT_FALSE"
                        print("Analysis failed: timeout. Results saved.")
                        break
                    with open(result_path + "/" + file_name.replace(".c","")+".c", "r") as f:
                        llvm_c = f.read()
                    with open(result_path + "/" + file_name.replace(".c","")+".txt", "r") as f:
                        ultimate_answer = f.read()
                        if ultimate_answer.find("RESULT: Ultimate proved your program to be correct!") != -1:
                            final_result = "TRUE"
                            true_cnt = true_cnt+1
                            result_dict[file_name]=result_dict[file_name] +"TRUE_Initial_"+str(llm_stage)+"_iterate_"+str(j)
                            print("Analysis succeeded: program terminates. Results saved.")
                            
                            analyze_finish = 1
                            break                    
                    j = j+1
                    if j >= jmax:
                        break
                   # -------------------------------- CounterExample --------------------------------
                    cex_list = extract_counterexample(ultimate_answer)
                    _tPrompt = generate_counterexample_prompt(llvm_c,cex_list)
                    result_dict[file_name] = result_dict[file_name] + "_COUNTER"+str(j)+" "
                    result = ""
                    result, in_tok, out_tok, t_used = call_llm_with_retry(_tPrompt)
                    log_llm_interaction(file_name, _tPrompt, result)   # Record log
                    total_input_tokens += in_tok
                    total_output_tokens += out_tok
                    total_analysis_time += t_used
                    if result == None:
                        result = ""
                    result = result.replace("```c","")
                    result = result.replace("```","")
                    save_string_to_file(result +"\n",result_path + "/" + file_name.replace(".c","")+".c")
        result_dict[file_name] += f"\t{total_input_tokens}\t{total_output_tokens}\t{total_analysis_time:.2f}\t{final_result}"
        save_dict_to_txt(result_dict,result_path + "/result_dict.txt")
    
    print(f"Analysis completed for {i+1} files. {true_cnt} programs proved to terminate.")

def log_llm_interaction(base_filename, prompt, response):
    """
    Append prompt and response to a log file named after base_filename.
    The file is saved in the result_path directory with extension .llm_log.txt
    """
    log_file = os.path.join(result_path, f"{base_filename}.llm_log.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"TIMESTAMP: {time.ctime()}\n")
        f.write("-" * 40 + " PROMPT " + "-" * 40 + "\n")
        f.write(prompt + "\n")
        f.write("-" * 40 + " RESPONSE " + "-" * 39 + "\n")
        f.write(response if response is not None else "ERROR: No response (None)\n")
        f.write("=" * 80 + "\n\n")

def generate_code_Infill(file_name,_tLoop, _TAG):
    if _TAG == 1:
        with open(result_path + "/" + file_name, "r") as f:
            file_open = f.read()
    else:
        with open(data_path + "/" + file_name, "r") as f:
            file_open = f.read()
    file_save =open(result_path + "/" + file_name,"w")
    head_line = """#include <stdlib.h>\n"""
    file_save.write(head_line+"\n")
    _leftCnt = 0
    _rightCnt = 0
    _findLoop = False
    _assertInsert = False
    _whileInsert = False
    define_line = "// >>> Infill Define <<<"
    assert_line = "// >>> Infill Assert <<<"
    update_line = "// >>> Infill Update End <<<"
    replace_line = "// >>> Infill Update Begin <<<"
    for lines in file_open.splitlines():
        if lines.replace(" ","").find("externvoid__VERIFIER_assert(bool);")!=-1:
            continue
        if lines.replace(" ","").find("void__VERIFIER_assert(intcond){if(!(cond)){ERROR:__VERIFIER_error();}}")!=-1:
            continue
        if lines.replace(" ","").find("typedefenum{false,true}bool;")!=-1:
            continue

        if lines == _tLoop:
            _findLoop = True
            lines = define_line +"\n"+lines
        if _findLoop == True:
            if ("while" in lines or "for" in lines) and _whileInsert == False:
                lines = lines+"\n"+replace_line+"\n"
                _whileInsert = True
            if "{" in lines:
                _leftCnt+=1
            if "}" in lines:
                _rightCnt+=1
            if _leftCnt == _rightCnt and _rightCnt != 0 and _assertInsert == False:
                _assertInsert = True
                lines = update_line+"\n"+assert_line+"\n"+lines
        
        file_save.write(lines+"\n")
    file_save.close()
    with open(result_path + "/" + file_name, "r") as f:
        file_save = f.read()
    return True

def run_termination_command(c_path, filename, ultimate_dir):
    c_path_no_ext = c_path.replace(".c", "")
    
    ULTIMATE_DIR = ultimate_dir
    ultimate_exec = f"{ULTIMATE_DIR}/Ultimate"
    toolchain = f"{ULTIMATE_DIR}/config/AutomizerReach.xml"
    settings = f"{ULTIMATE_DIR}/config/svcomp-Reach-64bit-Automizer_Default.epf"
    
    local_cmd = [
        ultimate_exec,
        "-tc", toolchain,
        "-s", settings,
        "-i", f"{c_path_no_ext}.c"
    ]
    
    print("Starting Ultimate locally with 60s timeout...")
    print("Command:", " ".join(local_cmd))
    start_time = time.time()
    completed = True
    output = ""
    
    process = None
    try:
        process = subprocess.Popen(
            local_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid 
        )
        # 使用 communicate 并设置超时
        stdout, stderr = process.communicate(timeout=60)
        output = stdout + stderr
        call_time = time.time() - start_time
        print(f"Ultimate execution completed within 60 seconds, time consumed: {call_time:.2f}s")
        
    except subprocess.TimeoutExpired:
        print(f"Ultimate execution timed out after 60 seconds, killing process group...")
        try:
            if process:
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGKILL)
                print(f"Killed process group {pgid}")
        except Exception as e:
            print(f"Failed to kill process group: {e}")
            if process:
                try:
                    process.kill()
                except:
                    pass
        if process:
            process.wait()
        output = f"Command timed out after 60 seconds and was forcefully terminated.\n"
        completed = False
        call_time = 60.0
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        output = f"Error: {str(e)}"
        completed = False
        call_time = time.time() - start_time
    
    # 4. 保存输出文件
    output_path = f"{result_path}/{filename}.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_string_to_file(output, output_path)
    

    print(f"[Stats] Ultimate call time: {call_time:.2f}s, Result: {'Success' if completed else 'Timeout'}")
    return completed, call_time

def main():
    parser = argparse.ArgumentParser()
    global llm_model
    global data_path
    global result_path
    global platform
    global api_key
    global url
    # Core parameters
    parser.add_argument('--llm-max', type=int, default=1, help='Maximum number of LLM analysis rounds')
    parser.add_argument('--iterate-max', type=int, default=1, help='Maximum number of iterations')
    parser.add_argument('--data-path', type=str, default=1, help='Path to input data')
    parser.add_argument('--result-path', type=str, default=1, help='Path to output results')
    parser.add_argument('--platform', type=str, default=1, help='LLM platform (deepseek, aliyun, openrouter)')
    parser.add_argument('--model', type=str, default=1, help='LLM model name')
    parser.add_argument('--ultimate-dir', type=str, required=True, 
                        help='Path to Ultimate tool directory, e.g., /workspace/UAutomizer-linux')
    args = parser.parse_args()
    print("-------------------------")
    print('LLM max rounds: ' + str(args.llm_max))
    print('LLM iterations: ' + str(args.iterate_max))
    print('Data path: ' + str(args.data_path))
    print('Result path: ' + str(args.result_path))
    print('Platform: ' + str(args.platform))
    print('Model: ' + args.model)
    platform = args.platform
    if args.platform not in ['deepseek', 'aliyun', 'openrouter']:
        print("Invalid platform. Choose one of: 'deepseek', 'aliyun', 'openrouter'")
        return
    with open('api_keys.json', 'r') as f:
        api_config = json.load(f)
    platform = args.platform
    if platform in api_config:
        api_key = api_config[platform]['api_key']
        url = api_config[platform]['url']
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    llm_model = args.model
    data_path = args.data_path
    result_path = args.result_path
    ultimate_dir = args.ultimate_dir
    print("-------------------------")
    
    process_c_files(data_path, args.llm_max, args.iterate_max, result_path, ultimate_dir)

    print("\nAnalysis completed. Results saved.")
   
if __name__ == "__main__":
    main()
