extern int __VERIFIER_nondet_int(void);

int main()
{
	int x;
	int y;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	while (x >= 0) {
		x = x + y;
		y = (-2)*y - 1;
	}
	return 0;
}
