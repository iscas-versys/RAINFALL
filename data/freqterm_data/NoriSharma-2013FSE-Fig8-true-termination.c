extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
  
  while (x >= y) {
    if (z > 1) {
      z = z - 1;
      x = x + z;
    } else {
      y = y + 1;
    }
  }
}
