// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Masse-VMCAI2014-Fig1a_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int a, b;
	a = __VERIFIER_nondet_int();
	b = __VERIFIER_nondet_int();
	while (a >= 0) {
		a = a + b;
		if (b >= 0) {
			b = -b - 1;
		} else {
			b = -b;
		}
	}
	return 0;
}