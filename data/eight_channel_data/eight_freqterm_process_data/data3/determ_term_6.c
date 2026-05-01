int main()
{
  int x = 8;
  int y = 9;
  int z = -2;
  
  while (x + y + z != 0){
    int oldx = x;
    x = -y + 1;
    y = 2*oldx + z;
    z = z*3;
  }
}
