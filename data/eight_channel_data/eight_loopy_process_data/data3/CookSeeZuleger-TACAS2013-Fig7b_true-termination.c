// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig7b_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, z;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	z = __VERIFIER_nondet_int();
	while (x>0 && y>0 && z>0) {
		if (__VERIFIER_nondet_int() != 0) {
			x = x - 1;
		} else {if (__VERIFIER_nondet_int() != 0) {
			y = y - 1;
			z = __VERIFIER_nondet_int();
		} else {
			z = z - 1;
			x = __VERIFIER_nondet_int();
		}}
	}
    return 0;
}