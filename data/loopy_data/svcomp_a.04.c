// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_a.04.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int c;
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    c = 0;
    while (x > y) {
        y = y + 1;
        c = c + 1;
    }
    return 0;
}