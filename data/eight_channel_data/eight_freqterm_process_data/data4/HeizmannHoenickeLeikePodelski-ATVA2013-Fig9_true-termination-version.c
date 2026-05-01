extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y, z;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  z = __VERIFIER_nondet_int();
  if (10*y > z && z < 10) {
    while (x >= 0) {
      x = x - 10*y + z;
    }
  }
  return 0;
}

