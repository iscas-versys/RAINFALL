// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.11_false-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, oldx;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    while (4*x - 5*y > 0) {
        oldx = x;
        x = 2*oldx + 4*y;
        y = 4*oldx;
    }
    return 0;
}