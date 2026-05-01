extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int N = __VERIFIER_nondet_int();

  if (y > 0) return 0;
  if (N <= 0) return 0;

  while (x != 0){
    if (x < N) x++; else x = y;
  }
}
