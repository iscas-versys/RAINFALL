// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_ex2.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int c, flag, x, y, z;
    c = 0;
    flag = 1;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    while ((y < z) && (flag > 0)) {
        if ((y > 0) && (x > 1)) {
            y = x*y;
        } else {
            if ((y > 0) && (x < -1)) {
                y = -x*y;
            } else {
                flag = 0;
            }
        }
        c = c + 1;
    }
    return 0;
}