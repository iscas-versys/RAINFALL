extern int __VERIFIER_nondet_int(void);

int main()
{
    int a, b, x, y;
    a = __VERIFIER_nondet_int();
    b = __VERIFIER_nondet_int();
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    if (a == b) {
      while (x >= 0 || y >= 0) {
        int tmp = x + a - b - 1;
        x = y + b - a - 1;
        y = tmp;
        int tmp2 = a;
        a = b;
        b = tmp2;
      }
    }
  return 0;
}
