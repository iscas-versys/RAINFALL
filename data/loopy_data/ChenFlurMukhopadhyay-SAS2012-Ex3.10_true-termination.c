// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex3.10_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    while (x >= 0 && x + y >= 0) {
        x = x + y + z;
        y = -z - 1;
    }
    return 0;
}