extern int __VERIFIER_nondet_int(void);

int main()
{
    int x;
    int y;
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
    if (x + y <= 0) { 
        while (x > 0) {
            x = x + y + 2;
            y = y - 1;
        }
    }
    return 0;
}
