// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.18_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    while (x > 0) {
        x = x + y - 5;
        y = -2*y;
    }
    return 0;
}