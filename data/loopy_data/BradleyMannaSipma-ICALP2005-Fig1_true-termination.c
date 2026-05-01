// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/BradleyMannaSipma-ICALP2005-Fig1_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int x, y, N;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	N = __VERIFIER_nondet_int();
	
	if (N < 536870912 && x < 536870912 && y < 536870912 && x >= -1073741824) {
    	if (x + y >= 0) {
	    	while (x <= N) {
		    	if (__VERIFIER_nondet_int() != 0) {
			    	x = 2*x + y;
				    y = y + 1;
    			} else {
	    			x = x + 1;
		    	}
		    }
	    }
	}
	return 0;
}