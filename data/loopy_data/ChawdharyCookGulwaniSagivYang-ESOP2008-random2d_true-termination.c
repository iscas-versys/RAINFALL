// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChawdharyCookGulwaniSagivYang-ESOP2008-random2d_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, i, r, N;
	N = 10;
    x = 0;
    y = 0;
    i = 0;
	while (i < N) {
		i = i + 1;
		r = __VERIFIER_nondet_int();
		if (r >= 0 && r <= 3) {
			if (r == 0) {
				x = x + 1;
			} else {if (r == 1) {
				x = x - 1;
			} else {if (r == 2) {
				y = y + 1;
			} else {if (r == 3) {
				y = y - 1;
            }}}}
		}
	}
	return 0;
}