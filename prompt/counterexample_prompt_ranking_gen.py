def generate_counterexample_ranking_gen_prompt(c_code, llvm):
    """
    生成包含反例信息的英语提示词
    
    参数:
        c_code (str): C 程序代码
        llvm (str): LLVM IR代码
        counterexample_values (list): 反例值列表
        counterexample_vars (list): 反例变量列表
        
    返回:
        str: 包含反例信息的英语提示词
    """
    # 构建完整的提示词
    prompt = (
    "You are a formal program analysis expert specializing in termination analysis.\n"
    "Your task is to re-judge the termination of the program by using counterexamples.\n"
    "Please provide me with a C-style definition of the ranking function(eg. int rank1 = ...;), never output explanations or additional text.\n"
    """IMPORTANT: Ranking function generation for multi-stage and lexicographical orders,
    Lexicographic: Requires that in each loop iteration, the tuple of ranking expressions strictly decreases in the lexicographic order, with all components remaining non-negative throughout the loop execution.
    Multi-Phase: Allows phased decrease where the first expression strictly decreases while positive, then the second expression takes over and strictly decreases while positive, and so on, until all become non-positive and the loop terminates."""
   
    
    "We used UAutomizer, and it found a counterexample demonstrating that our program is incorrect. \n"
    f"{llvm}\n\n"
    "Code with ranking function use UAutomizer to Analyze:\n"
    f"{c_code}\n\n"
    """I will provide you with several examples. 
    Code Input:
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
    Code Input:
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
    Code Input:
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
    \n
    Please provide me with a C-style definition of the ranking function(eg. int rank1 = ...;).
    All variables should be named with the prefix "ranki", not "new_ranki" or "old_ranki".
    """
    )   
    return prompt
