// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.03_assume.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    while (x > 0 && x > y) {
       y = y + x;
    }
    return 0;
}