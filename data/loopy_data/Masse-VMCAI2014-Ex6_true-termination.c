// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Masse-VMCAI2014-Ex6_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x >= 0) {
		x = x + y;
		if (y >= 0) {
			y = y - 1;
		}
	}
	return 0;
}