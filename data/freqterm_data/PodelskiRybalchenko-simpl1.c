extern int __VERIFIER_nondet_int(void);

int main() {
  int x, y;
  x = __VERIFIER_nondet_int();
  y = __VERIFIER_nondet_int();
  int newx, newy;
  while (x > 0 && y > 0) {
    if (__VERIFIER_nondet_int() != 0) {
      
      newx = __VERIFIER_nondet_int();
      if (newx >= x) break;
      x = newx;
      
      newy = __VERIFIER_nondet_int();
      if (newy <= y) break;
      y = newy;
      
    } else {
      
      newy = __VERIFIER_nondet_int();
      if (newy >= y) break;
      y = newy;
      
    }
  }
  return 0;
}
