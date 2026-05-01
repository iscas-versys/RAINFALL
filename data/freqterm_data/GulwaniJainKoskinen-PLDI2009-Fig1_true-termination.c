extern int __VERIFIER_nondet_int(void);

int main() {
    int id, maxId, tmp;
    id = __VERIFIER_nondet_int();
    maxId = __VERIFIER_nondet_int();

    if(0 <= id && id < maxId) {
        tmp = id+1;
        while(tmp!=id) {
            if (tmp <= maxId) {
                tmp = tmp + 1;
            } else {
                tmp = 0;
            }
        }
    }

    return 0;
}
