// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaB2.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    
    while (x > y) {
        x = x-1;
        y = y+1;
    }
    
    return 0;
}