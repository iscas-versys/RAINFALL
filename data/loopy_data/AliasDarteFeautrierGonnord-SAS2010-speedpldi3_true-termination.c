// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-speedpldi3_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int i, j, m, n;
	n = __VERIFIER_nondet_int();
	m = __VERIFIER_nondet_int();
	if (m > 0 && n > m) {
		i = 0;
		j = 0;
		while (i < n) {
			if (j < m) {
				j = j + 1;
			} else {
				j = 0;
				i = i + 1;
			}
		}
	}
	return 0;
}