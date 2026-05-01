extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  while (x > 0 && y > 0) {
    int old_x = x;
    int old_y = y;
    if (0 == __VERIFIER_nondet_int()) {
      x = old_x - 1;
      y = old_x;
    } else {
      x = old_y - 2;
      y = old_x + 1;
    }
  }
  return 0;
}
