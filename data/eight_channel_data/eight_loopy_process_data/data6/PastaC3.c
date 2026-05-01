// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaC3.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    int z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    
    while (x < y) {
        if (x < z) {
            x = x+1;
        } else {
            z = z+1;
        }
    }
    
    return 0;
}