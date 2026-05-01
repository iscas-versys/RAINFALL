// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/NoriSharma-FSE2013-Fig8_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int c, u, v, w, x, y, z;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	z = __VERIFIER_nondet_int();
    u = x;
    v = y;
    w = z;
    c = 0;
    while (x >= y) {
    	c = c + 1;
    	if (z > 1) {
    		z = z - 1;
    		x = x + z;
    	} else {
    		y = y + 1;
    	}
    }
    return 0;
}