extern int __VERIFIER_nondet_int(void);

int main() {
    int x, y, oldx;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    while (4*x + y > 0) {
        oldx = x;
        x = -2*oldx + 4*y;
        y = 4*oldx;
    }
    return 0;
}
