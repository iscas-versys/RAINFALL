// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaB7.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    int z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    
    while (x > z && y > z) {
        x = x-1;
        y = y-1;
    }
    
    return 0;
}