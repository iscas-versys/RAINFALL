extern int __VERIFIER_nondet_int(void);

int main()
{
  int i = 1;
  int j = 1;
  int d = __VERIFIER_nondet_int();
  int b = __VERIFIER_nondet_int();
  
  if (b <= 1) return 0;
  if (b <= d) return 0;
  
  while (i >= j){
    i = i*d;
    j = j*b;
  }
}
