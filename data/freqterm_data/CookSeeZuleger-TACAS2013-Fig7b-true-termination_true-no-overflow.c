extern int __VERIFIER_nondet_int(void);

// GF: depointerized and beautified

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
    
  while (x > 0 && y > 0 && z > 0) {
    if (0 == __VERIFIER_nondet_int()) {
        x = x - 1;
    } else if (0 == __VERIFIER_nondet_int()) {
        y = y - 1;
        z = __VERIFIER_nondet_int();
    } else {
        z = z - 1;
        x = __VERIFIER_nondet_int();
    }
  }
}
