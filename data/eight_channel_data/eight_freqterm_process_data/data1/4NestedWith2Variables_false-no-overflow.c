extern int __VERIFIER_nondet_int(void);

int main()
{
    int a, b, olda;
    a = __VERIFIER_nondet_int();
    b = __VERIFIER_nondet_int();
    while (a > 0) {
      olda = a;
      a = 3*olda - 4*b;
      b = 4*olda + 3*b;
    }
    return 0;
}
