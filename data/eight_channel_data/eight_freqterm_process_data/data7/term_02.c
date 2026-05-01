extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();

  while (x > y && y > z){
    x = x-3;
    y = y-2;
    z = z-1;
  }
}
