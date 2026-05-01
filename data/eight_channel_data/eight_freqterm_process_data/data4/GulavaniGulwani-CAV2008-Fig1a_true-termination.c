extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y, z;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  z = __VERIFIER_nondet_int();
  while (x < y) {
    if (z > x) {
      x = x + 1;
    } else {
      z = z + 1;
    }
  }
  return 0;
}
