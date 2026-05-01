// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PlusSwap.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    int z;
    int res;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    res = 0;
    
    while (y > 0) {
        z = x;
        x = y-1;
        y = z;
        res = res+1;
    }
    
    res = res + x;
    
    return 0;
}