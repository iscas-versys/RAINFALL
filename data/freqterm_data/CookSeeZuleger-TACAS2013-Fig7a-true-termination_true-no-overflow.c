extern int __VERIFIER_nondet_int(void);

// GF: depointerized and beautified

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int d = __VERIFIER_nondet_int();
  
  while (x > 0 && y > 0 && d > 0) {
    if (0 == __VERIFIER_nondet_int()) {
      x = x - 1;
      d = __VERIFIER_nondet_int();
    } else {
      x = __VERIFIER_nondet_int();
      y = y - 1;
      d = d - 1;
    }
  }
}
