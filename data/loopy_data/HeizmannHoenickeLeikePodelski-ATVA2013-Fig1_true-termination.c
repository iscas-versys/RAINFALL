// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/HeizmannHoenickeLeikePodelski-ATVA2013-Fig1_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
	x = __VERIFIER_nondet_int();
	y = 23;
	while (x >= 0) {
		x = x - y;
		y = y + 1;
	}
	return 0;
}