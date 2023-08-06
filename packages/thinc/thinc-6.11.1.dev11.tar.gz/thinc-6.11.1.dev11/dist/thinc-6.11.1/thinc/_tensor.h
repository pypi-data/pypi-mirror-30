#include <type_traits>

template <std::intmax_t n>
struct Shape
{
    int[n] shape;
    static const int ndim = n;
};
