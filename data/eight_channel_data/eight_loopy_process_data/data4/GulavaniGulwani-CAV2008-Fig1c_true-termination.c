// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/GulavaniGulwani-CAV2008-Fig1c_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, i, n;
	x = __VERIFIER_nondet_int();
	i = __VERIFIER_nondet_int();
	n = __VERIFIER_nondet_int();
	while (x < n) {
		i = i + 1;
		x = x + 1;
	}
	return 0;
}