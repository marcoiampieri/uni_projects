### As a final examination project for our Computer Science for High Energy Physics course, we were tasked to write a program to graphically represent the Mandelbrot set, applying the concepts that were taught to us in both the C++ and cloud coumputing lectures thate made up the course

## Tasks:
- Writing a program that draws the Mandelbrot set and saves it as a _.png_ output
- Implementing parallel computing to achieve the same result
- Check the performance of the parallel computing version for different _grain_size_ values
- Uploading all the code on a Virtual Machine running on Googlge Cloud and granting the professors access to it via SSH.  

## Content:
- **build-o/**: release build created via CMake
- **build-d/**: developer build created via CMake
- **main.cpp**: "standard" code to draw the Mandelbrot set
- **main_par.cpp**: version that implements parallel computing
- **CMakeLists.txt**: CMake file used to compile the code
- **mandelbrot.png**: graphical representation of the Mandelbrot set produced as _.png_ output by _main_par.cpp_  

