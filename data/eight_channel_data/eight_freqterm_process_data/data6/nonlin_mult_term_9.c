extern int __VERIFIER_nondet_int(void);

int main()
{
  int j = __VERIFIER_nondet_int();
  int b = __VERIFIER_nondet_int();
  
  if (b <= 1) return 0;
  if (j < 1) return 0;

  while (j < 10){
     j = -2 * j * b;
  }
}
