extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  
  if (x < y) return 0;
  while (x != y){
    x--; y++;
    if (x < y) x = x + 15;
  }
}
