extern int __VERIFIER_nondet_int(void);

int main() {
  int i, j, a, b;
  i = __VERIFIER_nondet_int();
  j = __VERIFIER_nondet_int();
  a = __VERIFIER_nondet_int();
  b = __VERIFIER_nondet_int();
  while (i + j + a + b == 0) {
    if (__VERIFIER_nondet_int() == 0) i--; else j++;
    if (__VERIFIER_nondet_int() == 0) a = a - 2; else b = b + 2;
  }  
  return 0;
}
