// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Nyala-2lex_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
	int x, y;
	while (x >= 0 && y >= 0) {
		y = y - 1;
		if (y < 0) {
			x = x - 1;
			y = __VERIFIER_nondet_int();
		}
	}
    return 0;
}