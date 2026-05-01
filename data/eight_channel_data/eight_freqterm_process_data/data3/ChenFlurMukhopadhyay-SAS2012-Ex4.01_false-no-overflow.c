extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y, z, n;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  z = __VERIFIER_nondet_int();
  n = __VERIFIER_nondet_int();
  while (x + y >= 0 && x <= n) {
    x = 2*x + y;
    y = z;
    z = z + 1;
  }
  return 0;
}
