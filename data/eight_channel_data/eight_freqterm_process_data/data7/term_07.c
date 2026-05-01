extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = 0;
  
  while (x > 0){
    if (y == 2) x = x - 3; else x = x + 1;
    if (y == 2) y = 0; else y = y + 1;
  }
}
