// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_a.09_assume.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    while (y > 0 && x >= z) {
        z = z + y;
    }
    return 0;
}