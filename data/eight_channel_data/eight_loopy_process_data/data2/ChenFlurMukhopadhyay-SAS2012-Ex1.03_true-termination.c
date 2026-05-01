// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex1.03_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, oldx;
    x = __VERIFIER_nondet_int();
    while (x > 1 && -2*x == oldx) {
        oldx = x;
        x = __VERIFIER_nondet_int();
    }
    return 0;
}