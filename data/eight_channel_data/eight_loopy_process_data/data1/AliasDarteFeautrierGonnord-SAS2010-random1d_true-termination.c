// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-random1d_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int a, x, max;
	max = __VERIFIER_nondet_int();
	if (max > 0) {
		a = 0;
		x = 1;
		while (x <= max) {
			if (__VERIFIER_nondet_int() != 0) {
				a = a + 1;
			} else {
				a = a - 1;
            }
			x = x + 1;
		}
	}
	return 0;
}