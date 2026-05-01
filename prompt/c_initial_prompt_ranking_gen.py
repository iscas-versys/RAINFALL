def generate_c_termination_initial_ranking_gen(c_code,file_name):
    system_prompt = """
You are an expert in program verification and termination analysis. Your task is to analyze the following C program and determine if it terminates. If it terminates, please provide me with a C-style definition of the ranking function.

IMPORTANT: Ranking function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates.

I will provide you with several examples. 

    a.Terminating (Single):
    #include <stdlib.h>
    extern int __VERIFIER_nondet_int(void);
    int main() {
        int x, y;
        x = __VERIFIER_nondet_int();
        y = __VERIFIER_nondet_int();
        while (x + y > 0) {
            x = x - 1;
            y = -2*y;
        }
        return 0;
    }
    llm Output:
        int rank1 = (x + y > 0) ? ( (x < 0) ? (y - x) : (x + 1) ) : 0;
    b.Terminating (Lexicographic). Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution:
    #include <stdlib.h>

    extern int __VERIFIER_nondet_int(void);

    int main() {
        int x = __VERIFIER_nondet_int();
        int y = __VERIFIER_nondet_int();
        int c1 = 0;
        int c2 = 0;

        while (x > y) {

            x = x + c1 / 3;
            y = y + c2 / 2;
            c1 = c1 + 2;
            c2 = c2 + 3;
        }
        return 0;
    }
    llm Output:
        int rank1 = x - y;                      
        int rank2 = (c1 == 0 && c2 == 0) ? 2 : 1; 
    c. Terminating (Multi-phase). Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates:
    #include <stdlib.h>

    extern int __VERIFIER_nondet_int(void);

    int main() {
        int a = __VERIFIER_nondet_int();
        int b = __VERIFIER_nondet_int();
        if (a <= 0 || b <= 0) {
            return 0;
        }

        while (a > 0 || b > 0) {

            if (a > 0 && b > 0) {
                a--;
                b--;
            } else if (a > 0) {
                a--;
            } else {
                b--;
            }
        }
        return 0;
    }
    llm Output:
        int rank1 = a + b;
        int rank2 = b;
Now, analyze the program and provide the appropriate response. Output only the C-style definition of the ranking function. Do not include any other text, comments, or explanations in your response.\n
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
