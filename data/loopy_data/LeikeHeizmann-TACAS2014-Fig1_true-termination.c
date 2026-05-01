// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LeikeHeizmann-TACAS2014-Fig1_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int q, y;
	q = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (q > 0) {
		q = q - y;
		y = y + 1;
	}
	return 0;
}