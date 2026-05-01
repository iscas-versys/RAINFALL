//GF: depointerized

extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  int z = __VERIFIER_nondet_int();
  if (0 == __VERIFIER_nondet_int()) {
    x = 1;
  } else {
    x = -1;
  }
  while (y < 100 && z < 100) {
    y = y + x;
    z = z - x;
  }
  return 0;
}
