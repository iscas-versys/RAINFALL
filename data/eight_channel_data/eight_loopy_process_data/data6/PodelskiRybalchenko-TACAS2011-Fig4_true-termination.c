// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PodelskiRybalchenko-TACAS2011-Fig4_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
	int x, y;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x > 0 && y > 0) {
		if (__VERIFIER_nondet_int() != 0) {
			x = x - 1;
			y = __VERIFIER_nondet_int();
		} else {
			y = y - 1;
		}
	}
	return 0;
}