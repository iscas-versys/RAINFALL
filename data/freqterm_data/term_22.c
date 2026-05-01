extern int __VERIFIER_nondet_int(void);

int main() {
  int K, x, y;
  K = __VERIFIER_nondet_int();
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();

  while (y != K) {
    if (x > K) {
      x = x - 1;
    } else if (x < K) {
      x = x + 1;
    } else x = K + 1;
    if (y > x) {
      y = y - 1;
    } else if (y < x) {
      y = y + 1;
    }
  }
  return 0;
}
