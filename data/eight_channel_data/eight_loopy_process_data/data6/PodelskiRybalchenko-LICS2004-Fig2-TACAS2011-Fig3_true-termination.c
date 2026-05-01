// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PodelskiRybalchenko-LICS2004-Fig2-TACAS2011-Fig3_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, oldx, oldy;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x > 0 && y > 0) {
		oldx = x;
		oldy = y;
		if (__VERIFIER_nondet_int() != 0) {
			x = oldx - 1;
			y = oldx;
		} else {
			x = oldy - 2;
			y = oldx + 1;
		}
	}
	return 0;
}