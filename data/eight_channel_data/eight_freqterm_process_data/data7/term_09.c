extern int __VERIFIER_nondet_int(void);

int main() {
  int K, x, y;
  K = __VERIFIER_nondet_int();
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  if (!(x < y)) return 0;

  while (y != K) {
    if (x == y) {
      if (x > K) {
        x = x - 1;
      } else {
        x = x + 1;
      }
      y = x;
    } else {
      y = y - 1;
    }
  }
  return 0;
}
