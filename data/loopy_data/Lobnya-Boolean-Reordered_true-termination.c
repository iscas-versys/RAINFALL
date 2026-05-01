// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Lobnya-Boolean-Reordered_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main ()
{
    int x, b;
	x = __VERIFIER_nondet_int();
	b = __VERIFIER_nondet_int();
	while (b != 0) {
		b = __VERIFIER_nondet_int();
		x = x - 1;
        if (x >= 0) {
            b = 1;
        } else {
            b = 0;
        }
	}
	return 0;
}