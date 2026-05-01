extern int __VERIFIER_nondet_int(void);

int main()
{
  int j = __VERIFIER_nondet_int();
  int b = __VERIFIER_nondet_int();
  
  if (b <= 1) return 0;
  
  while (j < 100){
    if (j <= 0) j = 1;
    else j = j*b;
  }
}
