cmake_minimum_required(VERSION 3.16)
project(isekai LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(ISEKAI_SOURCES src/main.cpp src/gltf_loader.cpp src/soft_raster.cpp src/soft_extra.cpp
    src/game_world.cpp src/game_hero.cpp src/game_scene.cpp src/game_procedural.cpp)

if(WIN32)
  # Zero third-party DLLs: native Win32 window + WGL OpenGL 3.3 (dynamic loader). Only system libs are linked.
  add_executable(isekai WIN32 ${ISEKAI_SOURCES} src/app.cpp src/win32_gl_window.cpp src/gl_renderer.cpp src/gl_hud.cpp)
  target_link_libraries(isekai PRIVATE opengl32 gdi32 user32 kernel32 shell32 winmm)
  if(MSVC)
    set_property(TARGET isekai PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded")  # static CRT: no vcruntime DLLs needed
    target_compile_definitions(isekai PRIVATE _CRT_SECURE_NO_WARNINGS)
  else()
    target_link_options(isekai PRIVATE -static -static-libgcc -static-libstdc++)
  endif()
else()
  add_executable(isekai ${ISEKAI_SOURCES})
endif()
target_include_directories(isekai PRIVATE include third_party src)

if(MSVC)
  target_compile_options(isekai PRIVATE /W3 /O2 /utf-8)
else()
  target_compile_options(isekai PRIVATE -Wall -Wextra -O2)
endif()
