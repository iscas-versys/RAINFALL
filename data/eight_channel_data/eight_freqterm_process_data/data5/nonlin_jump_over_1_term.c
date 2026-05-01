extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();

  if (y <= 1) return 0;

  while (x >= y) {
    if (x % y == 1) x++;
      else x = x - 2;
  }
  return 0;
}

