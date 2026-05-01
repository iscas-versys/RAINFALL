extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  if (x <= 0 || y <= 0) return 0;
  
  while (x + y > 0) {
    x = -4*x + 18;
    y = -6*y + 13;
  }
  return 0;
}
