extern int __VERIFIER_nondet_int(void);

int main()
{
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  
  while (x / 50 == y) {
    
    x = x + 51;
    y = y + 1;
    
  }
  return 0;
}
