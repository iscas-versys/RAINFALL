// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/BradleyMannaSipma-CAV2005-Fig1_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main() {
    int y1, y2;
	y1 = __VERIFIER_nondet_int();
	y2 = __VERIFIER_nondet_int();
	if (y1 > 0 && y2 > 0) {
    	while (y1 != y2) {
	    	if (y1 > y2) {
		    	y1 = y1 - y2;
    		} else {
	    		y2 = y2 - y1;
		    }
	    }
	}
	return 0;
}