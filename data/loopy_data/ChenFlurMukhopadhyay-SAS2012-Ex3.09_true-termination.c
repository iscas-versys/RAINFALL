// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex3.09_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z, oldx;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    while (x > 0 && x < y && x > 2*oldx) {
        oldx = x;
        x = __VERIFIER_nondet_int();
        y = z;
    }
    return 0;
}