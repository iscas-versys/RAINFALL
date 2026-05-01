def generate_c_termination_initial_without_fewshot(c_code,file_name):
    system_prompt = """
You are an expert in program verification and termination analysis. Your task is to analyze the following C program and determine if it terminates. If it terminates, modify the code only at the exact locations marked with: // >>> Infill Define <<<, // >>> Infill Update Begin <<<, // >>> Infill Update End <<<, // >>> Infill Assert <<<. Do not modify any other part of the code; only replace or add code at these specific markers.

IMPORTANT: Ranking function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates.

For each marker:
    At // >>> Infill Define <<<, replace it with necessary variable declarations for ranking variables (e.g., int old_rank; int new_rank = <ranking function expression>;) before loops.
    At // >>> Infill Update Begin <<<, replace it with code to save the old values of ranking variables at the beginning of each loop iteration (e.g., old_rank = new_rank;).
    At // >>> Infill Update End <<<, replace it with code to update the ranking variables after modifying the relevant program variables (e.g., new_rank = <ranking function expression>;), the expression for the ranking function must be consistent with its definition.
    At // >>> Infill Assert <<<, insert assertions ensuring that the ranking function strictly decreases, remains non-negative while the loop guard holds, and that the loop guard is false whenever the ranking function is negative.
    This is the assertion format for rank functions that are non-negative, non-increasing, and combined with the loop guard:

    Single assertion format:  
        //@ assert(old_rank1 > new_rank1 && old_rank1 >= 0);  
        //@ assert(new_rank1 >= 0 || !(guard));  

    Lexicographic assertion format:  
    //@ assert((( old_rank1 > new_rank1) || ( old_rank1 == new_rank1 && old_rank2 > new_rank2)) && old_rank1 >= 0  && old_rank2 >= 0);  
    //@ assert((new_rank1 >= 0  && new_rank2 >= 0) || !(guard));  

    Multi-Phase assertion format:  
    //@ assert((old_rank1 >= 0 && old_rank1 > new_rank1 ) || (new_rank1 < 0 && old_rank1 < 0 && old_rank2 >=0 && old_rank2 > new_rank2));  
    //@ assert((new_rank2 >= 0) || !(guard));

Important: Always include non-negativity checks for all ranking variables, where assertions start with the prefix //@ in the form of UAutomizer.

After making these changes, output the entire C program code with these modifications. 

Now, analyze the program and provide the appropriate response. Output only the modified code. Do not include any other text, comments, or explanations in your response.\n
"""

    user_prompt = (
        "Conduct formal termination analysis for this C program:\n"
        f"{c_code}\n"
        "Variable names should use the prefixes old_rank and new_rank, with a numeric index appended (e.g., old_rank1, new_rank1, old_rank2, new_rank2).\n"
        "Please ensure that the expressions generated at the `// >>> Infill Define <<<` and `// >>> Infill Update End <<<` positions are consistent.\n"
        "You must strictly follow the lexicographic order and multi-phase format for generating assertions as shown in the assertion format.\n"
        "Provide code."
    )

    # 合并系统提示和用户提示
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt
