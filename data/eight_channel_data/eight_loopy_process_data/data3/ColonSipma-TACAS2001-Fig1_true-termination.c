// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ColonSipma-TACAS2001-Fig1_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int k, i, j, tmp;
	k = __VERIFIER_nondet_int();
    i = __VERIFIER_nondet_int();
    j = __VERIFIER_nondet_int();
	while (i <= 100 && j <= k) {
		tmp = i;
		i = j;
		j = tmp + 1;
		k = k - 1;
	}
	return 0;
}