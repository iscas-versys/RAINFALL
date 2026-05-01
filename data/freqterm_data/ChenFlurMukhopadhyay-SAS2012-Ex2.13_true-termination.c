extern int __VERIFIER_nondet_int(void);

int main() {
    int x, y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    while (x - y > 0) {
        x = y - x;
        y = y + 1;
    }
    return 0;
}
