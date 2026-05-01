// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/HeizmannHoenickeLeikePodelski-ATVA2013-Fig2_true-termination.c


extern int __VERIFIER_nondet_int(void);

int main() {
	int y = __VERIFIER_nondet_int();
	int x = y + 42;
	while (x >= 0) {
		y = 2*y - x;
		x = (y + x) / 2;
	}
	return 0;
}