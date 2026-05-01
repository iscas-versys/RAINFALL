// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-terminate_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int i, j, k, ell;
	i = __VERIFIER_nondet_int();
	j = __VERIFIER_nondet_int();
	k = __VERIFIER_nondet_int();
	while (i <= 100 && j <= k) {
		ell = i;
		i = j;
		j = ell + 1;
		k = k - 1;
	}
	return 0;
}