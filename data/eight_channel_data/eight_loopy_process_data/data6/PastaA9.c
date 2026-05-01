// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaA9.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    int z;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    z = __VERIFIER_nondet_int();
    
    if (y > 0) {
        while (x >= z) {
            z = z+y;
        }
    }
    
    return 0;
}