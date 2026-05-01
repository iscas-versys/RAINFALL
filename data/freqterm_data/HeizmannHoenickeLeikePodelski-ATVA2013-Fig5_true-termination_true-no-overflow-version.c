extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = 3;
  while (x >= 0) {
    x = x - y;
    y = (y + 2) / 3;
  }
  return 0;
}

