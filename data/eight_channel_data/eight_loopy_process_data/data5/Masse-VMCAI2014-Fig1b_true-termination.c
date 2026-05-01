// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Masse-VMCAI2014-Fig1b_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
	int x;
    x = __VERIFIER_nondet_int();
	while (x <= 100) {
		if (__VERIFIER_nondet_int() != 0) {
			x = -2*x + 2;
		} else {
			x = -3*x - 2;
		}
	}
	return 0;
}