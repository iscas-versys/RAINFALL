// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/min_rf_true-termination.c


extern int __VERIFIER_nondet_int(void);



int main()
{
    int x,y;
    int z;
   
    x = __VERIFIER_nondet_int();
    y = __VERIFIER_nondet_int();
   
    while (y > 0 && x > 0) {
      if (x>y) {
          z = y;
      } else {
          z = x;
      }
      if (__VERIFIER_nondet_int() != 0) {
          y = y+x;
          x = z-1;
          z = y+z;
      } else {
          x = y+x;
          y = z-1;
          z = x+z;
      }
    }
    return 0;
}