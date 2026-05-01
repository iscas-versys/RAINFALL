// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LeikeHeizmann-TACAS2014-Ex8_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int q, y;
	q = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (q > 0) {
		if (y > 0) {
			y = 0;
			q = __VERIFIER_nondet_int();
		} else {
			y = y - 1;
			q = q - 1;
		}
	}
	return 0;
}