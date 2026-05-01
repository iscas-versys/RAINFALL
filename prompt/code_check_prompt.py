error_information_dict = {
    2:"IMPORTANT: In your previous attempt, the code placed at first marker (i.e., // >>> Infill Define <<<) failed to properly align with the desired variable declarations. This led to mismatched variable sets. To avoid such issues, I will provide the complete previously incorrectly generated code (including assertions) for this task. Please carefully analyze these materials to ensure that your completeness verification correctly enforces.",
    3:"IMPORTANT: In your previous attempt, the code placed at second marker (i.e., // >>> Infill Update Begin <<<) failed to properly align with the desired variable initializations. This led to missing initializations. To avoid such issues, I will provide the complete previously incorrectly generated code (including assertions) for this task. Please carefully analyze these materials to ensure that your completeness verification correctly enforces.",
    4:"IMPORTANT: In your previous attempt, the code placed at third marker (i.e., // >>> Infill Update End <<<) failed to properly align with the desired variable updates. This led to inconsistent expressions. To avoid such issues, I will provide the complete previously incorrectly generated code (including assertions) for this task. Please carefully analyze these materials to ensure that your completeness verification correctly enforces."
}

def generate_code_prompt(c_code, llm_c_code,error_information,code_error_information):

    system_prompt = """
You are an expert in program verification and termination analysis. Your task is to analyze the following C program and determine if it terminates. If it terminates, modify the code only at the exact locations marked with: // >>> Infill Define <<<, // >>> Infill Update Begin <<<, // >>> Infill Update End <<<, // >>> Infill Assert <<<. Do not modify any other part of the code; only replace or add code at these specific markers.

IMPORTANT: Rank function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates.

For each marker:
    At // >>> Infill Define <<<, replace it with necessary variable declarations for ranking variables (e.g., int old_rank1; int new_rank1;) before loops.
    At // >>> Infill Update Begin <<<, replace it with code to save the old values of ranking variables at the beginning of each loop iteration (e.g., old_rank1 = new_rank1;).
    At // >>> Infill Update End <<<, replace it with code to update the ranking variables after modifying the relevant program variables (e.g., new_rank1 = ...;).
    At // >>> Infill Assert <<<, insert assertions ensuring that the ranking function strictly decreases, remains non-negative while the loop guard holds, and that the loop guard is false whenever the ranking function is negative.

Important: Always include non-negativity checks for all ranking variables, where assertions start with the prefix //@ in the form of UAutomizer.\n"""f"{error_information}\n""""After making these changes, output the entire C program code with these modifications. 

I will provide you with several examples. 

    a.Terminating (Single):
    #include <stdlib.h>
    int main() {
        int x, y;
        x = __VERIFIER_nondet_int();
        y = __VERIFIER_nondet_int();

        int old_rank1;
        int new_rank1 = (x + y > 0) ? ( (x < 0) ? (y - x) : (x + 1) ) : 0;

        while (x + y > 0) {

            old_rank1 = new_rank1;
            
            x = x - 1;
            y = -2*y;

            new_rank1 = (x + y > 0) ? ( (x < 0) ? (y - x) : (x + 1) ) : 0;

            //@ assert(old_rank1 > new_rank1 && old_rank1 >= 0);
            //@ assert(new_rank1 >= 0 || !(x+y > 0));
        }
        return 0;
    }

    b.Terminating (Lexicographic). Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution:
    #include <stdlib.h>

    extern int __VERIFIER_nondet_int(void);

    int main() {
        int x = __VERIFIER_nondet_int();
        int y = __VERIFIER_nondet_int();
        int c1 = 0;
        int c2 = 0;

        int old_rank1, old_rank2;
        int new_rank1 = x - y;                      
        int new_rank2 = (c1 == 0 && c2 == 0) ? 2 : 1; 

        while (x > y) {

            old_rank1 = new_rank1;
            old_rank2 = new_rank2;

            x = x + c1 / 3;
            y = y + c2 / 2;
            c1 = c1 + 2;
            c2 = c2 + 3;

            new_rank1 = x - y;
            new_rank2 = (c1 == 0 && c2 == 0) ? 2 : 1;

            //@ assert(((old_rank1 > new_rank1) || (old_rank1 == new_rank1 && old_rank2 > new_rank2)) && old_rank1 >= 0  && old_rank2 >= 0);
            //@ assert((new_rank1 >= 0  && new_rank2 >= 0) || !(x > y));
        }
        return 0;
    }

    c. Terminating (Multi-phase). Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates:
    #include <stdlib.h>

    extern int __VERIFIER_nondet_int(void);

    int main() {
        int a = __VERIFIER_nondet_int();
        int b = __VERIFIER_nondet_int();
        if (a <= 0 || b <= 0) {
            return 0;
        }

        int old_rank1, old_rank2;
        int new_rank1 = a + b;
        int new_rank2 = b;


        while (a > 0 || b > 0) {

            old_rank1 = new_rank1;
            old_rank2 = new_rank2;

            if (a > 0 && b > 0) {
                a--;
                b--;
            } else if (a > 0) {
                a--;
            } else {
                b--;
            }

            new_rank1 = a + b;
            new_rank2 = b;

            //@ assert((old_rank1 >= 0 && old_rank1 > new_rank1) || (new_rank1 < 0 && old_rank1 < 0 && old_rank2 >= 0 && old_rank2 > new_rank2));
            //@ assert((new_rank2 >= 0) || !(a > 0 || b > 0));
        }
        return 0;
    }

Now, analyze the program and provide the appropriate response. Output only the modified code. Do not include any other text, comments, or explanations in your response.
"""

    user_prompt = (
        "Conduct formal termination analysis for this C program:\n"
        f"{c_code}\n"
        "previously incorrectly generated code (including assertions):\n"
        f"{llm_c_code}\n"
        "Specific reasons for failure:\n"
        f"{code_error_information}\n"
        "Please ensure that the expressions generated at the `// >>> Infill Define <<<` and `// >>> Infill Update End <<<` positions are consistent.\n"
        "Variable names should use the prefixes old_rank and new_rank, with a numeric index appended (e.g., old_rank1, new_rank1, old_rank2, new_rank2).\n"
        "You must strictly follow the lexicographic order and multi-phase format for generating assertions as shown in the example.\n"
        "Provide code."
    )

    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt
