# -*- coding: utf-8 -*-
"""Four-slot prompt without few-shot examples."""


def generate_c_termination_initial_without_fewshot(c_code, file_name):
    system_prompt = """
You are an expert in program verification and termination analysis. Your task is to analyze the following C program and determine if it terminates. If it terminates, modify the code only at the exact locations marked with: // >>> Infill Define <<<, // >>> Infill Update Begin <<<, // >>> Infill Update End <<<, // >>> Infill Assert <<<. Do not modify any other part of the code; only replace or add code at these specific markers.

IMPORTANT: Ranking function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates.

For each marker:
    At // >>> Infill Define <<<, declare the ranking variables before the loop and initialize every new_rankN with its ranking expression (e.g., int old_rank1; int new_rank1 = <ranking expression>;). Do not compute ranking values with if/else or loops here.
    At // >>> Infill Update Begin <<<, save the old values of the ranking variables at the beginning of each loop iteration (e.g., old_rank1 = new_rank1;).
    At // >>> Infill Update End <<<, update every new_rankN after the program variables have been modified, using exactly the same expression as in the declaration (e.g., new_rank1 = <ranking expression>;).
    At // >>> Infill Assert <<<, insert the assertions for the chosen ranking class, replacing guard with the loop condition exactly as written in the while statement. The assertions must be plain statements, not nested inside if statements.

Assertion formats.
    Single:
        //@ assert(old_rank1 > new_rank1 && old_rank1 >= 0);
        //@ assert(new_rank1 >= 0 || !(guard));
    Lexicographic (extend the tuple if you use more components):
        //@ assert(((old_rank1 > new_rank1) || (old_rank1 == new_rank1 && old_rank2 > new_rank2)) && old_rank1 >= 0 && old_rank2 >= 0);
        //@ assert((new_rank1 >= 0 && new_rank2 >= 0) || !(guard));
    Multi-Phase:
        //@ assert((old_rank1 >= 0 && old_rank1 > new_rank1) || (new_rank1 < 0 && old_rank1 < 0 && old_rank2 >= 0 && old_rank2 > new_rank2));
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
        "You must strictly follow the lexicographic order and multi-phase format for generating assertions.\n"
        "Provide code."
    )

    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt
