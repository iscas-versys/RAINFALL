extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  while (x + y > 0) {
    x = -5*x + 18;
    y = -6*y + 13;
  }
  return 0;
}
