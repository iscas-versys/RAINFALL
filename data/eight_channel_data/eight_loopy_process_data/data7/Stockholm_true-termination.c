// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Stockholm_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main()
{
    int x;
    int a;
    int b;
    x = __VERIFIER_nondet_int();
    a = __VERIFIER_nondet_int();
    b = __VERIFIER_nondet_int();
    if (a == b) {
        while (x >= 0) {
            x = x + a - b - 1;
        }
    }
    return 0;
}