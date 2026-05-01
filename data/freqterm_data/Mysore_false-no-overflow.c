extern int __VERIFIER_nondet_int(void);

int main()
{
    int c, x;
	x = __VERIFIER_nondet_int();
	c = __VERIFIER_nondet_int();
	if (c >= 2) {
	    while (x + c >= 0) {
		    x = x - c;
		    c = c + 1;
	    }
    }
	return 0;
}
