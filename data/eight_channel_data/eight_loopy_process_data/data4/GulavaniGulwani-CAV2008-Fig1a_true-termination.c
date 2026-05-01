// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/GulavaniGulwani-CAV2008-Fig1a_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z, i;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	z = __VERIFIER_nondet_int();
	i = __VERIFIER_nondet_int();
	while (x < y) {
		i = i + 1;
		if (z > x) {
			x = x + 1;
		} else {
			z = z + 1;
		}
	}
	return 0;
}