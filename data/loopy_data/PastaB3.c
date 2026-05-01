// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaB3.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    
    if (x > 0) {
        while (x > y) {
            y = x+y;
        }
    }
    
    return 0;
}