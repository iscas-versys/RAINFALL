// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron1_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int i, j, an, bn;
	i = __VERIFIER_nondet_int();
	j = __VERIFIER_nondet_int();
	an = __VERIFIER_nondet_int();
	bn = __VERIFIER_nondet_int();
	while ((an >= i && bn >= j) || (an >= i && bn <= j) || (an <= i && bn >= j)) {
		if (an >= i && bn >= j) {
			if (__VERIFIER_nondet_int() != 0) {
				j = j + 1;
			} else {
				i = i + 1;
			}
		} else {if (an >= i && bn <= j) {
			i = i + 1;
		} else {if (an <= i && bn >= j) {
			j = j + 1;
		}}}
	}
	return 0;
}