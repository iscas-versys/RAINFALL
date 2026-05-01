// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/aaron2_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, tx;
	tx = __VERIFIER_nondet_int();
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x >= y && tx >= 0) {
		if (__VERIFIER_nondet_int() != 0) {
			x = x - 1 - tx;
		} else {
			y = y + 1 + tx;
		}
	}
	return 0;
}