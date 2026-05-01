// terminates after 18 iterations

int main() {
  int i, j, k;
  i = -7; j = 2; k = 8;
  while (i != j) {
    i = i + j - k;
    j = j * 2;
    k = k - 1;
  }
  
  return 0;
}
