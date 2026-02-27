#include <SFML/Graphics.hpp>
#include <complex>
#include <tbb/parallel_for.h>
#include <tbb/blocked_range2d.h>
#include <atomic>
#include <tbb/tick_count.h>
#include <fstream>
#include <iostream>

using Complex = std::complex<double>;

int mandelbrot(Complex const& c)
{
  int i = 0;
  auto z = c;
  for (; i != 256 && norm(z) < 4.; ++i) {
    z = z * z + c;
  }
  return i;
}

auto to_color(int k)
{
  return k < 256 ? sf::Color{static_cast<sf::Uint8>(10 * k), 0, 0}
                 : sf::Color::Black;
}

int main()
{
  std::atomic<int> task_count;
  sf::Color gridColor = sf::Color::White;

  int const display_width{800};
  int const display_height{800};

  Complex const top_left{-2.2, 1.5};
  Complex const lower_right{0.8, -1.5};
  auto const diff = lower_right - top_left;

  auto const delta_x = diff.real() / display_width;
  auto const delta_y = diff.imag() / display_height;

  sf::Image image;
  image.create(display_width, display_height);

  // List of grain sizes to test
  std::vector<int> grain_sizes = {8, 16, 32, 64, 128, 256};
  
  // Open results file
  std::ofstream results("results.txt");
  results << "GrainSize ExecutionTime TaskCount\n";
  
  for (int grain : grain_sizes) {
    task_count = 0; // Reset task count
    tbb::tick_count start = tbb::tick_count::now();

    tbb::parallel_for(
      tbb::blocked_range2d<int>(0, display_height, grain, 0, display_width, grain),
      [&](const tbb::blocked_range2d<int>& range) {

        task_count++; // Count each task

        //Debug segment
        //std::cout << "Processing block: (" 
        //<< range.rows().begin() << "-" << range.rows().end() << ", " 
        //<< range.cols().begin() << "-" << range.cols().end() << ")\n";

        
        for (int row = range.rows().begin(); row < range.rows().end(); ++row) {
            for (int column = range.cols().begin(); column < range.cols().end(); ++column) {
                auto k = mandelbrot(top_left + Complex{delta_x * column, delta_y * row});
                image.setPixel(column, row, to_color(k));
            }
        }

        // Draw a horizontal grid line at the top of each block
        for (int column = range.cols().begin(); column < range.cols().end(); ++column)
        image.setPixel(column, range.rows().begin(), gridColor);
        
        // Draw a vertical grid line at the left of each block
        for (int row = range.rows().begin(); row < range.rows().end(); ++row)
            image.setPixel(range.cols().begin(), row, gridColor);

      },
      tbb::simple_partitioner());

    tbb::tick_count end = tbb::tick_count::now();
    double elapsed_time = (end - start).seconds();
    
    results << grain << " " << elapsed_time << " " << task_count << "\n";
}
results.close();
image.saveToFile("mandelbrot.png");
}
