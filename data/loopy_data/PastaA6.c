// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaA6.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    int z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    
    while (x > y + z) {
        y = y+1;
        z = z+1;
    }
    
    return 0;
}