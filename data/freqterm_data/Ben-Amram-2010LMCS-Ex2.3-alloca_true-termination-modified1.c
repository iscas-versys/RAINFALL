
extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
  
  while (x > 0 && y > 0 && z > 0) {
    if (y > x) {
      y = z;
      z = __VERIFIER_nondet_int();
      x = z + 1;
    } else {
      z = z - 1;
      y = __VERIFIER_nondet_int();
      x = y + 1;
    }
  }
  return 0;
}
