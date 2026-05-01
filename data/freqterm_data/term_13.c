extern int __VERIFIER_nondet_int(void);

int main() {
    int i, j, k;
    i = __VERIFIER_nondet_int();
    j = __VERIFIER_nondet_int();
    k = __VERIFIER_nondet_int();
    while (i + j + k >= 0) {
        if (__VERIFIER_nondet_int() == 0) i--; else j++;
        k = k - 2;
    }  
    return 0;
}
