// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.09_assume.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int c;
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    c = 0;
    if (y > 0) {
        while (x > 0) {
            if (x > y) {
                x = y;
            } else {
                x = x - 1;
            }
            c = c + 1;
        }
    }
    return 0;
}