cmake_minimum_required(VERSION 3.15)
project(heic_to_jpeg LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(WIN32)
    add_executable(heic_to_jpeg main.cpp)
    target_link_libraries(heic_to_jpeg PRIVATE windowscodecs ole32 OleAut32)
else()
    message(WARNING "heic_to_jpeg è progettato specificamente per sistemi Windows tramite Windows Imaging Component (WIC).")
endif()

