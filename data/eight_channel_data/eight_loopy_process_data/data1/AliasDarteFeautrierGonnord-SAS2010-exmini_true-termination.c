// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-exmini_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int i, j, k, tmp;
	i = __VERIFIER_nondet_int();
	j = __VERIFIER_nondet_int();
	k = __VERIFIER_nondet_int();
	tmp = __VERIFIER_nondet_int();
	while (i <= 100 && j <= k) {
		tmp = i;
		i = j;
		j = tmp + 1;
		k = k - 1;
	}
	return 0;
}