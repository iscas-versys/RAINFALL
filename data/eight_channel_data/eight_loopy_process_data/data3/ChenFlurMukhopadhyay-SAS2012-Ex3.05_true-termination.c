// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex3.05_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    while (x >= 0 && x <= z) {
        x = 2*x + y;
        y = y + 1;
    }
    return 0;
}