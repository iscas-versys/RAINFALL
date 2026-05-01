// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.20_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    while (x > y && y >= 1 && y <= 2) {
        x = x - y;
        y = __VERIFIER_nondet_int();
    }
    return 0;
}