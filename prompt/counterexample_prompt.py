def generate_counterexample_prompt(c_code, llvm):

    prompt = (
    "You are a formal program analysis expert specializing in termination analysis.\n"
    "Your task is to re-judge the termination of the program by using counterexamples. Please modify the code of the above ranking function to a correct ranking function and output the complete verification code.\n"
    "Output only the code, never output explanations or additional text.\n"
    """IMPORTANT: Ranking function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates.
    IMPORTANT: Always include non-negativity checks for all ranking variables, where assertions start with the prefix //@ in the form of UAutomizer.\n"""
    "Variable names should use the prefixes old_rank and new_rank, with a numeric index appended (e.g., old_rank1, new_rank1, old_rank2, new_rank2).\n"
    "You must strictly follow the lexicographic order and multi-phase format for generating assertions as shown in examples.\n"
    "We used UAutomizer, and it found a counterexample demonstrating that our program is incorrect. \n"
    f"{llvm}\n\n"
    "Code with ranking function use UAutomizer to Analyze:\n"
    f"{c_code}\n\n"
    """I will provide you with several examples. 
    a.Terminating (Single):
    #include <stdlib.h>
    int main() {
        int x, y;
        x = __VERIFIER_nondet_int();
        y = __VERIFIER_nondet_int();

        int new_rank1 = (x + y > 0) ? ( (x < 0) ? (y - x) : (x + 1) ) : 0;
        int old_rank1;
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
    b.Terminating (Lexicographic). Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in lexicographic order, with all components remaining non-negative throughout the loop execution:
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
        int new_rank1 = a + b;
        int new_rank2 = b;
        int old_rank1, old_rank2;

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
    \n"""
    )   
    return prompt
