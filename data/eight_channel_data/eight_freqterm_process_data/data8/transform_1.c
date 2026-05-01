extern int __VERIFIER_nondet_int(void);

int main()
{
  int x, y, z;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  if (y <= 1) return 0;
  z = 0;
  while (x > 0) {
    x = x - y;
    y = y - z;
    if (z == 0) z = 13;
      else if (z == 13) z = -20;
        else if (z == -20) z = 7;
          else z = 0;
  }
  return 0;
}
