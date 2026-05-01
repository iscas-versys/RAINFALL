extern int __VERIFIER_nondet_int(void);

int main()
{
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();

  while (x > y) {
    if (0 == __VERIFIER_nondet_int())      x = x - 1;
    else if (0 == __VERIFIER_nondet_int()) y = y + 1;
    else if (0 == __VERIFIER_nondet_int()) x = x - 2;
    else if (0 == __VERIFIER_nondet_int()) y = y + 2;
    else if (0 == __VERIFIER_nondet_int()) x = x - 3;
    else if (0 == __VERIFIER_nondet_int()) y = y + 3;
    else if (0 == __VERIFIER_nondet_int()) x = x - 4;
    else if (0 == __VERIFIER_nondet_int()) y = y + 4;
    else if (0 == __VERIFIER_nondet_int()) x = x - 5;
    else                                   y = y + 5;
  }
}
