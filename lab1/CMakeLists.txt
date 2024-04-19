cmake_minimum_required(VERSION 3.26)
project(sin)

set(CMAKE_CXX_STANDARD 17)

option(DOUBLE_PRECISION "Use double precision for array elements" OFF)

add_executable(sin main.cpp)

if(DOUBLE_PRECISION)
    target_compile_definitions(sin PRIVATE DOUBLE_PRECISION)
endif()