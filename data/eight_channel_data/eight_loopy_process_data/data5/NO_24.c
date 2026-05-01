// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/NO_24.c





int main() {
    int a;
    int b;
    a = 1;
    b = 2;
    
    while (a + b < 5) {
        a = a - b;
        b = a + b;
        a = b - a;
    }
    
    return 0;
}