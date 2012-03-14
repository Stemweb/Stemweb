#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
  double Kx,Ky,Kxy,minK,maxK;
  if (argc != 4)
    fprintf(stderr, "usage: %s <K(xy)> <K(x)> <K(y)>\n", argv[0]);
  else
  {
    Kxy=atof(argv[1]);
    Kx=atof(argv[2]);
    Ky=atof(argv[3]);
    if (Kx>=Ky)
    {
      maxK=Kx;
      minK=Ky;
    }
    else
    {
      maxK=Ky;
      minK=Kx;
    }
    printf("%f ", (Kxy-minK)/maxK);
  }
  return 0;
}
