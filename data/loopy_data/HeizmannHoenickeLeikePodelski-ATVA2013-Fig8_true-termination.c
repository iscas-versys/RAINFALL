// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/HeizmannHoenickeLeikePodelski-ATVA2013-Fig8_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	if (2*y >= 1) {
    	while (x >= 0) {
	    	x = x - 2*y + 1;
	    }
	}
	return 0;
}