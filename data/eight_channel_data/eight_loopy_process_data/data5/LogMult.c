// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LogMult.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
    int y;
    int res;
    x = __VERIFIER_nondet_int();
    y = 2;
    res = 1;
    
    if (x < 0 || y < 1) { }
    else {
        while (x > y) {
            y = y*y;
            res = 2*res;
        }
    }
    
    return 0;
}