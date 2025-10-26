#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
  
  srand(time(NULL));
  
   int number = (rand() % 100) + 1;
  int guess,attempts=0;
  
  do
  {
    printf("Enter a Guess: ");
    scanf("%d", &guess);
    attempts++;
    
    if (guess == number) 
    printf("You got it! YAY\n%d attempts",attempts);
    else if (guess < number) 
    printf("Too low!\n");
    else
    printf("too high!\n");
    
    
  } while (guess != number);
  
  return 0;
}