extern int __VERIFIER_nondet_int(void);

int main() {
  int x, n, b, t;
  x = __VERIFIER_nondet_int();
  n = __VERIFIER_nondet_int();
  b = __VERIFIER_nondet_int();
  if (b >= 1) {
    t = 1;
  } else {
    t = -1;
  }
  while (x <= n) {
    if (b >= 1) {
      x = x + t;
    } else {
      x = x - t;
    }
  }
  return 0;
}
