extern int __VERIFIER_nondet_int(void);

int main()
{
  int x, y, z, oldx;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  z = __VERIFIER_nondet_int();

  while (x >= 0 || y >= 0 || z >= 0) {
    oldx = x;
    x = y - 1;
    y = z - 1;
    z = oldx - 1;
  }
  return 0;
}
