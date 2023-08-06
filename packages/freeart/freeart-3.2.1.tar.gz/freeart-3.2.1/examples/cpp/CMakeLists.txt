# CMakeLists files in this project can
# refer to the root source directory of the project as ${HELLO_SOURCE_DIR} and
# to the root binary directory of the project as ${HELLO_BINARY_DIR}.
cmake_minimum_required (VERSION 2.8.11)
project (examples_cpp)

include_directories(${CMAKE_SOURCE_DIR}/freeart/core/include)
include_directories(${CMAKE_SOURCE_DIR}/freeart/core/src)
include_directories(${CMAKE_SOURCE_DIR}/freeart/cpp_utils)

# add all executables
add_executable(projector_tx projector_tx.cpp)
add_executable(projector_fluo projector_fluo.cpp)
add_executable(reconstr_tx reconstr_tx.cpp)
add_executable(reconstr_fluo reconstr_fluo.cpp)

# linking the library
target_link_libraries (projector_tx FreeART)
target_link_libraries (projector_fluo FreeART)
target_link_libraries (reconstr_tx FreeART)
target_link_libraries (reconstr_fluo FreeART)

SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -w" )

