// GF: depointerized

extern int __VERIFIER_nondet_int(void);

int main() {
  int x = __VERIFIER_nondet_int();
    while (x <= 100) {
        if (0 == __VERIFIER_nondet_int()) {
            x = - 2 * x + 2;
        } else if (0 == __VERIFIER_nondet_int()) {
            x = - 3 * x - 2;
        } else {
            x = - 4 * x + 2;
        }
    }
}
