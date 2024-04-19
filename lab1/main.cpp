#include <iostream>
#include <cmath>

#ifdef DOUBLE_PRECISION
using Type = double;
#else
using Type = float;
#endif

const int SIZE = 10000000;

int main() {
    Type* array = new Type[SIZE];
    for (int i = 0; i < SIZE; i++) {
        Type x = static_cast<Type>(i) / SIZE;
        array[i] = static_cast<Type>(std::sin(2 * M_PI * x));
    }
    Type sum = 0;
    for (int i = 0; i < SIZE; i++)
        sum += array[i];
    std::cout << sum << std::endl;
    return 0;
}