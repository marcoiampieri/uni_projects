### This project was the object of the final examination for our C++ course in Bologna

# Tasks:

- Write a code that correctly simulates the SIR (Susceptible, Infected, Removed) model, either by applying the model's equations or by implementing graphical representations
- Use the concepts shown during the course of the lectures
- (Optional) Implement extra features like lockdowns, vaccines, etc.

## Content:

- **pandemic.hpp**: here the _Person_ type and the _World_ class are declared, which are going to be the main components to build the initial representation grid,
   along with the _infection_, _removal_ and _spread_ functions, which change the structure of the grid with each passing "day"
- **pandemic.cpp**: where the _World_ class' constructor and methods are implemented
- **setting_functions.hpp**: where the functions used to set the initial configuration are declared
- **setting_functions.cpp**: where these functions are implemented, allowing to set parameters like the population's dimension, the duration of the pandemic, etc.
- **pandemic_test.cpp**: where some simple configurations are tested using _doctest.h_
- **main_pandemic.cpp**: where the _print_ functions is implemented, showing population grid in the output; _Susceptibles_ are represented with the character "**@**", _Infected_ with "*" and _Removed_ with an empty cell



Compiled with  g++ -Wall -Wextra -fsanitize=address  
Formatted using _clang-format_
