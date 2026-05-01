// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.05.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, tmp;
    x = __VERIFIER_nondet_int();
    tmp = __VERIFIER_nondet_int();
    while ((x > 0) && (x == 2*tmp)) {
        x = x - 1;
        tmp = __VERIFIER_nondet_int();
    }
    return 0;
}