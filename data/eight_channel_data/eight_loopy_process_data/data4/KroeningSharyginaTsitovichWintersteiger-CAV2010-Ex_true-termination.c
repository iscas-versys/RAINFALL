// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/KroeningSharyginaTsitovichWintersteiger-CAV2010-Ex_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int i;
	i = __VERIFIER_nondet_int();
	while (i < 255) {
		if (__VERIFIER_nondet_int() != 0) {
			i = i + 1;
		} else {
			i = i + 2;
		}
	}
	return 0;
}