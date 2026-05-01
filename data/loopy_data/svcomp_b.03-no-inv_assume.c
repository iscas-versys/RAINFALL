// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.03-no-inv_assume.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    if (x > 0) {
        while (x > y) {
            y = y + x;
        }
    }
    return 0;
}