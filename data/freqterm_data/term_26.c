extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();

  int c1 = 0;
  int c2 = 0;

  while (x == y){
    x = x + c1 % 2;
    y = y + c2 % 3;
    c1++; c2++;
  }
}
