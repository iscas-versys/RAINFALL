def generate_c_termination_initial_ranking_gen_without_few_shot(c_code,file_name):
    system_prompt = """
You are an expert in program verification and termination analysis. Your task is to analyze the following C program and determine if it terminates. If it terminates, please provide me with a C-style definition of the ranking function(eg. int rank1 = ...; int rank2 = ...).

IMPORTANT: Ranking function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates.

Now, analyze the program and provide the appropriate response. Output only the C-style definition of the ranking function(eg. int rank1 = ...; int rank2 = ...). Do not include any other text, comments, or explanations in your response.\n
"""

    user_prompt = (
        "Conduct formal termination analysis for this C program:\n"
        f"{c_code}\n"
        "Variable names should be named using the prefixes ranki.\n"
        "Provide code."
    )

    # 合并系统提示和用户提示
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt
