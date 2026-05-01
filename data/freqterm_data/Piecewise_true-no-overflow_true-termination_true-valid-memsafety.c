extern int __VERIFIER_nondet_int(void);

int main()
{
  int i, j;
  j = __VERIFIER_nondet_int();
  i = __VERIFIER_nondet_int();
  while (j > 0 && i > 0 && i != j) {
    if (j < i) {
      j = j - 1;
      i = __VERIFIER_nondet_int();
    } else if (i < j) {
      i = i - 1;
      j = __VERIFIER_nondet_int();
    }
  }
  return 0;
}
