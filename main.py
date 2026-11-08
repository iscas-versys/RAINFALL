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
from static_check.codeChecker import check_rank_consistency, preprocess_c_code
from static_check.rankingChecker import validate_c_file
from static_check.astChecker import check_AST
from pycparser import c_parser
from utils import *
from prompt import *
import clang
from clang.cindex import Index, CursorKind
api_key = ""

OFOX_IPS = ["8.218.173.249", "47.83.190.88", "47.83.144.71", "47.76.128.166"]
OFOX_PROXY = "socks5://172.17.0.1:17891"

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
    if platform == "oxoai":
        payload = {
            "model": llm_model,
            "messages": [{"role": "user", "content": iterate_prompt}],
            "temperature": 0.0,
        }
    try:
        start_time = time.time()
        if platform == "oxoai":
            from curl_cffi import requests as cffi_requests, CurlOpt
            stream_payload = dict(payload, stream=True,
                                  stream_options={"include_usage": True})
            last_err = None
            for ip in OFOX_IPS:
                chunks = []
                input_tokens = output_tokens = 0
                try:
                    resp = cffi_requests.post(
                        url=url,
                        headers=headers,
                        data=json.dumps(stream_payload),
                        impersonate="chrome",
                        proxies={"http": OFOX_PROXY, "https": OFOX_PROXY},
                        curl_options={CurlOpt.RESOLVE: ["api.ofox.ai:443:" + ip],
                                      CurlOpt.LOW_SPEED_LIMIT: 1,
                                      CurlOpt.LOW_SPEED_TIME: 45},
                        timeout=900,
                        stream=True,
                    )
                    if resp.status_code != 200:
                        last_err = "status %d on %s: %s" % (
                            resp.status_code, ip, resp.text[:300])
                        continue
                    last_data = time.time()
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        text = line.decode() if isinstance(line, bytes) else line
                        if not text.startswith("data: "):
                            if time.time() - last_data > 120:
                                raise RuntimeError("no tokens for 120s")
                            continue
                        last_data = time.time()
                        text = text[6:].strip()
                        if text == "[DONE]":
                            break
                        try:
                            event = json.loads(text)
                        except json.JSONDecodeError:
                            continue
                        if event.get("usage"):
                            usage = event["usage"]
                            input_tokens = usage.get("prompt_tokens", input_tokens) or input_tokens
                            output_tokens = usage.get("completion_tokens", output_tokens) or output_tokens
                        choices = event.get("choices") or []
                        if choices:
                            delta = choices[0].get("delta") or {}
                            if delta.get("content"):
                                chunks.append(delta["content"])
                    call_time = time.time() - start_time
                    content = "".join(chunks)
                    think_end = content.rfind("</think>")
                    if think_end != -1:
                        content = content[think_end + len("</think>"):]
                    return content, input_tokens, output_tokens, call_time
                except Exception as e:
                    last_err = "%s on %s" % (e, ip)
                    continue
            print(f"Request failed: {last_err}")
            return None, 0, 0, 0.0
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
    except Exception as e:
        if platform == "oxoai":
            print(f"Request failed: {str(e)}")
            return None,0,0,0.0
        raise

def call_llm_with_retry(prompt, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        content, in_tok, out_tok, used_time = analyze_with_llm(prompt, **kwargs)
        if content is not None:
            return content, in_tok, out_tok, used_time
        print(f"LLM call failed (attempt {attempt+1}/{max_retries}), waiting and retrying...")
        time.sleep(2 ** attempt)  
    print("Max retries exhausted, abandoning this call")
    return None, 0, 0, 0.0   

GHOST_IDENTIFIER_RE = re.compile(r'\b(?:old_rank|new_rank)\w*')


def original_has_ghost_identifiers(path):
    """The input program must not already use the reserved ghost names."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
    except OSError:
        return False
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    return bool(GHOST_IDENTIFIER_RE.search(code))


def validate_candidate(original_path, candidate_text, scratch_path):
    """Run every static check on the same candidate text.

    Returns (ok, stage, payload). stage is one of ok/unsupported/code/ast/assert.
    """
    if original_has_ghost_identifiers(original_path):
        return False, 'unsupported', {
            'inf': 'The input program already uses old_rank/new_rank identifiers.'
        }
    try:
        with open(scratch_path, 'w', encoding='utf-8') as f:
            f.write(candidate_text)
    except OSError as exc:
        return False, 'unsupported', {'inf': 'Cannot write candidate: %s' % exc}

    status, info = check_rank_consistency(candidate_text)
    if status in (5, 6, 8):
        return False, 'unsupported', {'status': status, 'info': info}
    if status != 1:
        return False, 'code', {'status': status, 'info': info}

    ok, msg = check_AST(original_path, scratch_path)
    if not ok:
        return False, 'ast', {'msg': msg}

    ok, msg = validate_c_file(candidate_text)
    if not ok:
        return False, 'assert', {'msg': msg}

    count = info.get('count', 1) if isinstance(info, dict) else 1
    return True, 'ok', {'count': count}


def _mask_c(text):
    """Replace comments, string/char literals, and directive lines with spaces."""
    out = list(text)
    i, n = 0, len(text)
    line_start = True
    while i < n:
        ch = text[i]
        if ch == '/' and i + 1 < n and text[i + 1] == '/':
            while i < n and text[i] != '\n':
                out[i] = ' '
                i += 1
            continue
        if ch == '/' and i + 1 < n and text[i + 1] == '*':
            out[i] = out[i + 1] = ' '
            i += 2
            while i < n and not (text[i] == '*' and i + 1 < n and text[i + 1] == '/'):
                if text[i] != '\n':
                    out[i] = ' '
                i += 1
            if i < n:
                out[i] = out[i + 1] = ' '
                i += 2
            continue
        if ch in ('"', "'"):
            quote = ch
            out[i] = ' '
            i += 1
            line_start = False
            while i < n:
                if text[i] == '\\':
                    out[i] = ' '
                    i += 1
                    if i < n:
                        if text[i] != '\n':
                            out[i] = ' '
                        i += 1
                    continue
                if text[i] == quote:
                    out[i] = ' '
                    i += 1
                    break
                if text[i] != '\n':
                    out[i] = ' '
                i += 1
            continue
        if ch == '#' and line_start:
            while i < n and text[i] != '\n':
                out[i] = ' '
                i += 1
            continue
        if ch == '\n':
            line_start = True
        elif not ch.isspace():
            line_start = False
        i += 1
    return ''.join(out)


def _find_loop_body(masked):
    """Return (start, end) of the first loop body's inner text, or None."""
    match = re.search(r'\b(?:while|for)\s*\(', masked)
    if not match:
        return None
    open_paren = masked.index('(', match.start())
    depth = 0
    close_paren = None
    for i in range(open_paren, len(masked)):
        ch = masked[i]
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                close_paren = i
                break
    if close_paren is None:
        return None
    j = close_paren + 1
    while j < len(masked) and masked[j].isspace():
        j += 1
    if j >= len(masked) or masked[j] != '{':
        return None
    depth = 0
    for k in range(j, len(masked)):
        if masked[k] == '{':
            depth += 1
        elif masked[k] == '}':
            depth -= 1
            if depth == 0:
                return j + 1, k
    return None


def _pick_label(masked):
    base = '__rainfall_continue'
    label = base
    suffix = 0
    while re.search(r'\b%s\b' % re.escape(label), masked):
        suffix += 1
        label = '%s_%d' % (base, suffix)
    return label


def cover_continues(text, update_count):
    """Rewrite `continue` to `goto label` and place the label before the final updates."""
    masked = _mask_c(text)
    body = _find_loop_body(masked)
    if body is None:
        return None, 'cannot locate a braced loop body'
    label = _pick_label(masked)

    start, end = body
    edits = [(start + m.start(), start + m.end())
             for m in re.finditer(r'\bcontinue\b', masked[start:end])]
    if not edits:
        return text, ''
    for begin, finish in reversed(edits):
        text = text[:begin] + 'goto %s' % label + text[finish:]

    masked = _mask_c(text)
    body = _find_loop_body(masked)
    if body is None:
        return None, 'cannot relocate the loop body after rewriting continue'

    inner = text[body[0]:body[1]]
    lines = inner.splitlines(keepends=True)
    starts = []
    position = body[0]
    for line in lines:
        starts.append(position)
        position += len(line)

    update_re = re.compile(r'^\s*new_rank\d+\s*=.*;\s*$')
    seen = 0
    target = None
    for index in range(len(lines) - 1, -1, -1):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith('//@'):
            continue
        if update_re.match(stripped):
            seen += 1
            target = starts[index]
            if seen == update_count:
                break
        else:
            break
    if target is None or seen < update_count:
        return None, 'cannot find the final %d new_rank update statements' % update_count

    indent = re.match(r'[ \t]*', text[target:]).group(0)
    text = text[:target] + indent + label + ': ;\n' + text[target:]

    masked = _mask_c(text)
    body = _find_loop_body(masked)
    if body is None or re.search(r'\bcontinue\b', masked[body[0]:body[1]]):
        return None, 'a continue statement is still present after rewriting'
    return text, ''


def syntax_ok(text):
    try:
        c_parser.CParser().parse(preprocess_c_code(text, verbose=False), filename='<candidate>')
        return True
    except Exception as exc:
        print("Syntax check failed after instrumentation: %s" % exc)
        return False


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
                while j < jmax:
                    if result == "":
                        result_dict[file_name]=result_dict[file_name] +"_LLM_FALSE"+str(j)+" "
                        break

                    if j > 1:
                        print(f"Analysis attempt {j-1}:")

                    scratch_path = result_path + "/" + file_name
                    ok_candidate, stage, payload = validate_candidate(file_path, result, scratch_path)
                    if not ok_candidate:
                        if stage == 'unsupported':
                            if payload.get('status') in (5, 6):
                                result_dict[file_name] = (result_dict[file_name]
                                                          + "_LLM_FALSE" + str(j) + " ")
                            else:
                                result_dict[file_name] = result_dict[file_name] + "_UNSUPPORTED"
                            print("Candidate uses an unsupported construct; stopping this loop.")
                            break

                        j = j + 1
                        result_dict[file_name] = result_dict[file_name] + {
                            'ast': "_AST_FALSE", 'code': "_code_FALSE",
                            'assert': "_ASSERT_FALSE",
                        }[stage] + str(j) + " "
                        if j >= jmax:
                            break

                        if stage == 'ast':
                            print("AST check FALSE!")
                            prompt = generate_ASTERROR_prompt(_tccode, result, payload['msg'])
                        elif stage == 'code':
                            status = payload['status']
                            rank_inf = payload['info']
                            print("code check FALSE! status:", status)
                            if isinstance(rank_inf, dict) and 'errors' in rank_inf:
                                combined_str = '\n'.join(rank_inf['errors'])
                            elif isinstance(rank_inf, dict):
                                combined_str = rank_inf.get('inf', '')
                            else:
                                combined_str = str(rank_inf)
                            prompt = generate_code_prompt(
                                _tccode, result, error_information_dict[status], combined_str)
                        else:
                            print("check Ranking function FALSE!")
                            prompt = generate_RankingFucntion_prompt(_tccode, result, payload['msg'])

                        result, in_tok, out_tok, t_used = call_llm_with_retry(prompt)
                        log_llm_interaction(file_name, prompt, result)
                        total_input_tokens += in_tok
                        total_output_tokens += out_tok
                        total_analysis_time += t_used
                        if result is None:
                            result = ""
                            break
                        print("LLM feedback received, waiting for Ultimate verification...")
                        result = result.replace("```c","").replace("```","")
                        save_string_to_file(result +"\n",result_path + "/" + file_name)
                        continue

                    print("All static checks passed; covering continue statements...")
                    transformed, cover_msg = cover_continues(result, payload['count'])
                    if transformed is None:
                        result_dict[file_name] = result_dict[file_name] + "_UNSUPPORTED"
                        print("Continue rewrite failed: " + cover_msg)
                        break
                    if not syntax_ok(transformed):
                        result_dict[file_name] = result_dict[file_name] + "_UNSUPPORTED"
                        break
                    result = transformed
                    save_string_to_file(result +"\n",result_path + "/" + file_name)
                    save_string_to_file(result +"\n",result_path + "/" + file_name.replace(".c","_"+str(j)+"_.c"))
                   # -------------------------------- UAutomizer CHECK --------------------------------
                    ultimate_result,ultimate_time  = run_termination_command(result_path + "/" + file_name,file_name.replace(".c",""),ultimate_dir)
                    total_analysis_time += ultimate_time
                    if ultimate_result == False:
                        import subprocess
                        subprocess.run(["pkill", "z3"])
                        j = j + 1
                        result_dict[file_name] = (result_dict[file_name]
                                                  + "_TIMELIMIT_FALSE" + str(j) + " ")
                        if j >= jmax:
                            print("Analysis failed: timeout and no iteration left.")
                            break
                        print("Ultimate timed out; restarting with a fresh initial query "
                              "(iteration %d/%d)." % (j, counter_max))
                        initial_prompt = generate_c_termination_initial(_tccode, file_name)
                        result, in_tok, out_tok, t_used = call_llm_with_retry(initial_prompt)
                        log_llm_interaction(file_name, initial_prompt, result)
                        total_input_tokens += in_tok
                        total_output_tokens += out_tok
                        total_analysis_time += t_used
                        if result is None:
                            result = ""
                            break
                        result = result.replace("```c", "").replace("```", "")
                        save_string_to_file(result + "\n", result_path + "/" + file_name)
                        continue
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
    parser.add_argument('--platform', type=str, default=1, help='LLM platform (deepseek, aliyun, openrouter, oxoai)')
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
    if args.platform not in ['deepseek', 'aliyun', 'openrouter', 'oxoai']:
        print("Invalid platform. Choose one of: 'deepseek', 'aliyun', 'openrouter', 'oxoai'")
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
