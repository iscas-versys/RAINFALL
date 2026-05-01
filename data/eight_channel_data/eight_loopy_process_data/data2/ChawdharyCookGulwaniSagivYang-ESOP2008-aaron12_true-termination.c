// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron12_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	z = __VERIFIER_nondet_int();
	while (x >= y) {
		if (__VERIFIER_nondet_int() != 0) {
			x = x + 1;
			y = y + x;
		} else {
			x = x - z;
			y = y + (z * z);
			z = z - 1;
		}
	}
	return 0;
}