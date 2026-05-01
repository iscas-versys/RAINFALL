extern int __VERIFIER_nondet_int(void);

// GF: depointerized

int main() {
    int x = __VERIFIER_nondet_int();
    int y = __VERIFIER_nondet_int();
    int z;

    while (y > 0 && x > 0) {
        if (x > y) z = y;
        else z = x;
        if (0 == __VERIFIER_nondet_int()) {y = y + x; x = z - 1; z = y + z; }
        else {x = y + x; y = z - 1; z = x + z; }
    }
}
