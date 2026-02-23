#ifndef LIFE_WORLD_HPP
#define LIFE_WORLD_HPP

#include <cassert>
#include <vector>

namespace life {

enum class Cell : char { Dead, Alive };

class World
{
  using Grid = std::vector<Cell>;
  int m_side;
  Grid m_grid;

 public:
  World(int n) : m_side(n), m_grid(m_side * m_side, Cell::Dead)
  {
  }
  int side() const
  {
    return m_side;
  }
  Cell const& cell(int r, int c) const noexcept
  {
    auto const i = (r + m_side) % m_side;
    auto const j = (c + m_side) % m_side;
    assert(i >= 0 && i < m_side && j >= 0 && j < m_side);
    auto const index = i * m_side + j;
    assert(index >= 0 && index < static_cast<int>(m_grid.size()));
    return m_grid[index];
  }
  Cell& cell(int r, int c) noexcept
  {
    auto const i = (r + m_side) % m_side;
    auto const j = (c + m_side) % m_side;
    assert(i >= 0 && i < m_side && j >= 0 && j < m_side);
    auto const index = i * m_side + j;
    assert(index >= 0 && index < static_cast<int>(m_grid.size()));
    return m_grid[index];
  }

  friend bool operator==(World const& l, World const& r)
  {
    return l.m_grid == r.m_grid;
  }
};

inline int neighbours_alive(World const& world, int r, int c)
{
  int result = -static_cast<int>(world.cell(r, c));
  for (int i : {-1, 0, 1}) {
    for (int j : {-1, 0, 1}) {
      result += static_cast<int>(world.cell(r + i, c + j));
    }
  }
  return result;
}

inline World evolve(World const& current)
{
  int const N = current.side();

  World next(N);

  for (int i = 0; i != N; ++i) {
    for (int j = 0; j != N; ++j) {
      int const c = neighbours_alive(current, i, j);
      if (c == 3) {
        next.cell(i, j) = Cell::Alive;
      } else if (c == 2) {
        next.cell(i, j) = current.cell(i, j);
      }
    }
  }

  return next;
}

}  // namespace life

#endif
