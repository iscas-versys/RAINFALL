extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = 1;
  int y = __VERIFIER_nondet_int();
  
  if (y <= 1) return 0;
  
  while (x < 10000){
    x = x * y;
  }
}
