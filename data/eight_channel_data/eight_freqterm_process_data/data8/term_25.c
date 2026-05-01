extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
  int w = x + y + z;
  int c = 0;
  
  while (w == x + y + z){
    if (c < 100) y --;
    c++;
    x = x + y + c;
    z = z - y;
  }
}

