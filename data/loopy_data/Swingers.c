// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Swingers.c





int main() {
    int bob;
    int samantha;
    int temp;
    bob = 13;
    samantha = 17;
    
    while (bob + samantha < 100) {
        temp = bob;
        bob = samantha;
        samantha = temp;
    }
    
    return 0;
}