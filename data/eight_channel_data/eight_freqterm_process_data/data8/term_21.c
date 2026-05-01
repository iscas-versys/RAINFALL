extern int __VERIFIER_nondet_int(void);

int main()
{
  int z = __VERIFIER_nondet_int();
  
  while (z >= 0) {
    if (z % 5 == 0) z = z - 5;
      else z++;
  }
  return 0;
}
