extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = 5;
  
  if (x <= 10) return 0;
  
  while (x != 2*y) {
    if (x % 5 == 1) x++;
      else x = x - 2;
  }
  return 0;
}
