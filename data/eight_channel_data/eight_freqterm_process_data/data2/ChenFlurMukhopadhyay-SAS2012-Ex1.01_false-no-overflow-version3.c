extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  while (x < 0 && y > 0) {
    x = -3*x - 17;
    y = -4*y + 8;
  }
  return 0;
}
