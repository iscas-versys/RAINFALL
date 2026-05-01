extern int __VERIFIER_nondet_int(void);

int main()
{
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  
  while (x / 50 == y) {
    
    int z = __VERIFIER_nondet_int();
    x = x + 1 + 50*z;
    y = y + z;
    
  }
  return 0;
}
