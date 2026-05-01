// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/HeizmannHoenickeLeikePodelski-ATVA2013-Fig6_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x >= 0 && y >= 1) {
		x = x - y;
		y = __VERIFIER_nondet_int();
	}
	return 0;
}