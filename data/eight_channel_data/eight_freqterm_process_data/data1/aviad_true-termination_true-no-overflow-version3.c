extern int __VERIFIER_nondet_int(void);

int main() {
    int a = __VERIFIER_nondet_int();
    while (a > 1) {
      if (a % 10 == 0) a = a / 10;
        else a = a - 1;
    }
    return 0;
}
