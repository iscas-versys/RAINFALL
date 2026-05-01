extern int __VERIFIER_nondet_int(void);

int main() {
	int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
	while (x > 0 && y > 0) {
		y = y - x;
		if (y < 0) {
			x = x - 1;
			y = __VERIFIER_nondet_int();
		}
	}
  return 0;
}
