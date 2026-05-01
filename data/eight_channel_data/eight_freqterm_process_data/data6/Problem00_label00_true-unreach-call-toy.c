int calculate_output(int);
extern int __VERIFIER_nondet_int(void);
extern void exit(int);

	int a7 = 0;

	int calculate_output(int input) {
    a7++;
    if (a7 == 10) return 0; else return input - 1;
	}

int main()
{
    // default output
    int output = -1;

    a7 = 0;

    // main i/o-loop
    while(output != 0){
        // read input
        int input = __VERIFIER_nondet_int();
        if ((input != 1) && (input != 2) && (input != 3) && (input != 4) && (input != 5) && (input != 6)) return -2;

        // operate eca engine
        output = calculate_output(input);
    }
}
