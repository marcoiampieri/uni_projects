#include <chrono>
#include <iostream>
#include <random>
#include <thread>
#include "world.hpp"

void print(std::ostream& os, life::World const& world)
{
  constexpr auto clear = "\033[2J";
  const auto N = world.side();

  os << clear;
  os << '+' << std::string(N, '-') << "+\n";
  for (int r = 0; r != N; ++r) {
    os << '|';
    for (int c = 0; c != N; ++c) {
      os << (world.cell(r, c) == life::Cell::Alive ? '*' : ' ');
    }
    os << "|\n";
  }
  os << '+' << std::string(N, '-') << "+\n";
}

int main()
{
  constexpr int world_size = 30;

  life::World world(world_size);

  {
    std::default_random_engine eng{std::random_device{}()};
    std::uniform_int_distribution<int> dist{0, world_size - 1};

    for (int i = 0; i != world_size * world_size / 5; ++i) {
      auto r = dist(eng);
      auto c = dist(eng);
      for (; world.cell(r, c) == life::Cell::Alive;
           r = dist(eng), c = dist(eng))
        ;
      world.cell(r, c) = life::Cell::Alive;
    }
  }
  // initialize a "glider"
  // world.cell(28, 4) = life::Cell::Alive;
  // world.cell(29, 5) = life::Cell::Alive;
  // world.cell(30, 3) = life::Cell::Alive;
  // world.cell(30, 4) = life::Cell::Alive;
  // world.cell(30, 5) = life::Cell::Alive;

  for (int i = 0; i != 200; ++i) {
    world = evolve(world);
    print(std::cout, world);
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  }
}
