# Build steps
file(GLOB_RECURSE PoloParser_SOURCES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
*.cpp)

add_executable(polo-parser ${PoloParser_SOURCES})

target_link_libraries(
    polo-parser
    "/usr/local/lib/libclang.dylib"
)

include_directories(
  ${PROJECT_SOURCE_DIR}/inc
)
