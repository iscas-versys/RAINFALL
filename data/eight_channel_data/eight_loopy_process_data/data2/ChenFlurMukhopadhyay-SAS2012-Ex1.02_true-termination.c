// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex1.02_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, oldx;
    x = __VERIFIER_nondet_int();
    while (x > 0 && x < 100 && x >= 2*oldx + 10) {
        oldx = x;
        x = __VERIFIER_nondet_int();
    }
    return 0;
}