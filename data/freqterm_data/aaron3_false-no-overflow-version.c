extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y, z, tx;
	x = __VERIFIER_nondet_int();
	y = __VERIFIER_nondet_int();
	z = __VERIFIER_nondet_int();
	tx = __VERIFIER_nondet_int();
	while (x >= y && x <= tx + z) {
			z = z - 1;
			tx = x;
			x = __VERIFIER_nondet_int();
	}
	return 0;
}
