extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  
  if (x <= y) return 0;
  if (y <= 1) return 0;
  
  while (x > y){
    if (0 == __VERIFIER_nondet_int())
      x = x % y;
    else
      x = x - y;
  }
}
