extern int __VERIFIER_nondet_int(void);

int main()
{
    int x, y, a, b;
    a = __VERIFIER_nondet_int();
    b = __VERIFIER_nondet_int();
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    if (a == b + 1 && x < 0) {
        while (x >= 0 || y >= 0) {
          x = x + a - b - 1;
          y = y + b - a - 1;
        }
    }
    return 0;
}
