// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig8a_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x;
	x = __VERIFIER_nondet_int();
	while (x != 0) {
		if (x > 0) {
			x = x - 1;
		} else {
			x = x + 1;
		}
	}
	return 0;
}