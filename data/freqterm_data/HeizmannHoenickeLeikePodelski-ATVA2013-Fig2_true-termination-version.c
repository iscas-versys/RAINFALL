extern int __VERIFIER_nondet_int(void);

int main() {
  int y = __VERIFIER_nondet_int();
  int x = __VERIFIER_nondet_int();
  if (x > y) {
    while (x >= 0) {
      y = 2*y - x;
      x = (y + x + 1) / 2;
    }
  }
  return 0;
}
