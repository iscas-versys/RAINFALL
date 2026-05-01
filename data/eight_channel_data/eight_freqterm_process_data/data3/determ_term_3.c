int main() {
  int x = 5;
  int y = 1;
  int z = 17;
  
  while (!(x == y && y == z)) {
    x = x + 1;
    y = y * 2;
    z = z - 3;
  }
  return 0;
}

