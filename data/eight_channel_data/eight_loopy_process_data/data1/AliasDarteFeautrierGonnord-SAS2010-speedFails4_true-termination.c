// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-speedFails4_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int i, x, n, b, t;
	i = __VERIFIER_nondet_int();
	x = __VERIFIER_nondet_int();
	n = __VERIFIER_nondet_int();
	b = __VERIFIER_nondet_int();
	if (b >= 1) {
		t = 1;
	} else {
		t = -1;
    }
	while (x <= n) {
		if (b >= 1) {
			x = x + t;
		} else {
			x = x - t;
		}
	}
	return 0;
}