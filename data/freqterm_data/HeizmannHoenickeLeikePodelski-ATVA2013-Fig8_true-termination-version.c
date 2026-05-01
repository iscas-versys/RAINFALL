extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  if (5*y >= 1) {
    while (x >= 0) {
      x = x - 4*y + 3;
    }
  }
  return 0;
}

