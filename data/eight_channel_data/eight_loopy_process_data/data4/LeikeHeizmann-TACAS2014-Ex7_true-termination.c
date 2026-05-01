// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LeikeHeizmann-TACAS2014-Ex7_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int q, z;
	q = __VERIFIER_nondet_int();
	z = __VERIFIER_nondet_int();
	while (q > 0) {
		q = q + z - 1;
		z = -z;
	}
	return 0;
}