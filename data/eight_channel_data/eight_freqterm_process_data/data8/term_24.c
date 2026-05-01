extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
  
  if (x > z || y > z) return 0;
  while (x != y){
    x++; y++;
    if (x > z) x = z;
    if (y > z) y = y - 1;
  }
}
