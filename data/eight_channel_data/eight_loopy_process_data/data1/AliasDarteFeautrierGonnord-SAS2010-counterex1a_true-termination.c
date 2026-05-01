// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-counterex1a_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, n, b;
	n = __VERIFIER_nondet_int();
	b = __VERIFIER_nondet_int();
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x >= 0 && 0 <= y && y <= n) {
		if (b == 0) {
			y = y + 1;
			if (__VERIFIER_nondet_int() != 0) {
				b = 1;
            }
		} else {
			y = y - 1;
			if (__VERIFIER_nondet_int() != 0) {
				x = x - 1;
				b = 0;
			}
		}
	}
	return 0;
}