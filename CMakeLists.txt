cmake_minimum_required(VERSION 3.20)
project(F95Checker VERSION 12.0.0)

include(CMakeDependentOption)
option(F95CHECKER_VENDORED_CURL                    "Statically build and link cURL, will not require cURL on target system to run"         ON)
option(F95CHECKER_VENDORED_WOLFSSL                 "Statically build and link wolfSSL, will not require wolfSSL on target system to run"   ON)
option(F95CHECKER_VENDORED_SDL3                    "Statically build and link SDL3, will not require SDL3 on target system to run"         ON)
option(F95CHECKER_VENDORED_SQLITE3                 "Statically build and link SQLite3, will not require SQLite3 on target system to run"   ON)
option(F95CHECKER_PYTHON_VENV                      "Use a dedicated python venv instead of system python, requirements are auto-installed" ON)

# Directories
set(F95CHECKER_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(BUILD_DIR "${F95CHECKER_DIR}/build")
set(SRC_DIR "${F95CHECKER_DIR}/src")
set(LIB_DIR "${F95CHECKER_DIR}/lib")
set(FONTS_DIR "${LIB_DIR}/fonts")
set(ICONS_DIR "${LIB_DIR}/icons")
set(VENDOR_DIR "${LIB_DIR}/vendor")
set(RESOURCES_DIR "${F95CHECKER_DIR}/resources")
set(VENV_DIR "${CMAKE_CURRENT_BINARY_DIR}/venv")
set(GLAD_DIR "${LIB_DIR}/glad")
set(BC7E_DIR "${LIB_DIR}/bc7e")
set(SHLEX_DIR "${LIB_DIR}/shlex")
set(GLAD_GEN "${VENDOR_DIR}/glad")
set(BC7E_GEN "${VENDOR_DIR}/bc7e")
set(SDL3_DIR "${VENDOR_DIR}/sdl3")
set(CURL_DIR "${VENDOR_DIR}/curl")
set(CWALK_DIR "${VENDOR_DIR}/cwalk")
set(IMGUI_DIR "${VENDOR_DIR}/imgui")
set(DCIMGUI_DIR "${LIB_DIR}/dcimgui")
set(JSONC_DIR "${VENDOR_DIR}/json-c")
set(SQLITE3_DIR "${VENDOR_DIR}/sqlite3")
set(WOLFSSL_DIR "${VENDOR_DIR}/wolfssl")
set(SHLEXCPP_DIR "${VENDOR_DIR}/shlex_cpp")
set(WOLFSSL_CFG "${VENDOR_DIR}/wolfssl_config")
set(DEARBINDINGS_DIR "${VENDOR_DIR}/dear_bindings")

# Export compilation DB
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
file(CREATE_LINK "${CMAKE_CURRENT_BINARY_DIR}" "${BUILD_DIR}/current" SYMBOLIC)

# Global compiler flags
add_compile_options(-fexceptions)  # Interop with C++ exceptions
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-O0)  # Better debugging experience
endif()
add_compile_options(-Werror)  # Fail on any warning

# Build vendored libs statically
set(BUILD_STATIC_LIBS ON CACHE BOOL "ALL STATIC")
set(BUILD_SHARED_LIBS OFF CACHE BOOL "NO SHARED")

# Global includes
# Allows #include <dcimgui/dcimgui.h> instead of just #include <dcimgui.h>
include_directories("${SRC_DIR}" "${LIB_DIR}" "${VENDOR_DIR}")

# Main sources
# Globbing is discouraged but fine when keeping in mind its caveat:
# Adding new files won't be detected, need to run cmake again to detect them
# You can also `touch CMakeLists.txt`, or save it without making changes
file(GLOB_RECURSE sources "${SRC_DIR}/*.c" "${SRC_DIR}/*.h")

# Main executable
add_executable(F95Checker "${sources}")

# Compiler flags
target_compile_options(F95Checker PRIVATE -std=gnu2x)  # Standard
target_compile_options(F95Checker PRIVATE -Wall -Wextra -Wstrict-prototypes -Wredundant-decls -Wundef)  # Warnings
target_compile_options(F95Checker PRIVATE -fdata-sections -ffunction-sections -fno-math-errno)  # Optimizations

# Metadata
target_compile_definitions(F95Checker PRIVATE F95CHECKER_VERSION="${CMAKE_PROJECT_VERSION}")  # Version

# Python (needed for GLAD and dear_bindings)
find_package(Python COMPONENTS Interpreter REQUIRED)
if(F95CHECKER_PYTHON_VENV)
    execute_process(COMMAND "${Python_EXECUTABLE}" -m venv "${VENV_DIR}")
    set(Python_EXECUTABLE "${VENV_DIR}/bin/python")
    foreach(requirements_dir IN ITEMS "${DEARBINDINGS_DIR}" "${GLAD_GEN}" "${ICONS_DIR}")
        execute_process(COMMAND "${Python_EXECUTABLE}" -m pip install -U -r "${requirements_dir}/requirements.txt")
        get_filename_component(requirements_name "${requirements_dir}" NAME)
        configure_file("${requirements_dir}/requirements.txt" "${VENV_DIR}/.${requirements_name}.installed")
    endforeach()
endif()

# OpenGL (via GLAD loader)
add_subdirectory("${GLAD_GEN}/cmake")
glad_add_library(glad STATIC EXCLUDE_FROM_ALL MERGE REPRODUCIBLE API gl:core=3.0 LOCATION "${GLAD_DIR}")
target_link_libraries(F95Checker PRIVATE glad)

# SDL3
if(F95CHECKER_VENDORED_SDL3)
    set(SDL_STATIC ON)
    set(SDL_AUDIO OFF)
    set(SDL_CAMERA OFF)
    set(SDL_DIALOG OFF)
    set(SDL_GPU OFF)
    set(SDL_HAPTIC OFF)
    set(SDL_POWER OFF)
    set(SDL_RENDER OFF)
    set(SDL_SENSOR OFF)
    add_subdirectory("${SDL3_DIR}" EXCLUDE_FROM_ALL)
    target_link_libraries(F95Checker PRIVATE SDL3-static)
else()
    find_package(SDL3 REQUIRED CONFIG REQUIRED COMPONENTS SDL3-shared)
    target_link_libraries(F95Checker PRIVATE SDL3::SDL3)
endif()

# ImGui (via dcimgui bindings)
set(DCIMGUI_BACKENDS sdl3 opengl3)
add_subdirectory("${DCIMGUI_DIR}")
if(F95CHECKER_VENDORED_SDL3)
    target_link_libraries(dcimgui PRIVATE SDL3-static)
else()
    target_link_libraries(dcimgui PRIVATE SDL3::SDL3)
endif()
target_link_libraries(dcimgui PRIVATE glad)
target_link_libraries(F95Checker PRIVATE dcimgui)

# Fonts (generate embedded C sources)
add_subdirectory("${FONTS_DIR}")
target_link_libraries(F95Checker PRIVATE fonts)

# Icons (generate embedded C sources)
add_subdirectory("${ICONS_DIR}")
target_link_libraries(F95Checker PRIVATE icons)

# SQLite
if(F95CHECKER_VENDORED_SQLITE3)
    add_subdirectory("${SQLITE3_DIR}" EXCLUDE_FROM_ALL)
    target_compile_options(sqlite3 PRIVATE -Wno-stringop-overread)
    target_link_libraries(F95Checker PRIVATE sqlite3)
else()
    find_package(SQLite3 REQUIRED)
    target_link_libraries(F95Checker PRIVATE SQLite::SQLite3)
endif()

# M*LIB
target_compile_definitions(F95Checker PRIVATE M_USE_SMALL_NAME=0)  # Disable legacy type/function names

# cwalk
add_subdirectory("${CWALK_DIR}" EXCLUDE_FROM_ALL)
target_link_libraries(F95Checker PRIVATE cwalk)

# json-c
add_subdirectory("${JSONC_DIR}" EXCLUDE_FROM_ALL)
target_link_libraries(F95Checker PRIVATE json-c)

# wolfSSL
if(F95CHECKER_VENDORED_WOLFSSL)
    include_directories("${WOLFSSL_CFG}")
    if(F95CHECKER_VENDORED_CURL)
        set(WOLFSSL_CURL ON)
    endif()
    add_subdirectory("${WOLFSSL_DIR}" EXCLUDE_FROM_ALL)
    target_compile_options(wolfssl PRIVATE -Wno-stringop-overflow)
    target_link_libraries(F95Checker PRIVATE wolfssl)
else()
    find_package(WolfSSL REQUIRED)
    target_link_libraries(F95Checker PRIVATE wolfssl)
endif()

# cURL
if(F95CHECKER_VENDORED_CURL)
    set(BUILD_CURL_EXE OFF)
    set(BUILD_STATIC_CURL ON)
    set(HTTP_ONLY ON)
    set(CURL_BROTLI "OFF" CACHE STRING "NO BROTLI")
    set(CURL_ZLIB "OFF" CACHE STRING "NO ZLIB")
    set(CURL_ZSTD "OFF" CACHE STRING "NO ZSTD")
    set(CURL_USE_LIBPSL OFF)
    set(CURL_USE_LIBSSH2 OFF)
    set(USE_LIBIDN2 OFF)
    set(USE_NGHTTP2 OFF)
    if(F95CHECKER_VENDORED_WOLFSSL)
        set(CURL_USE_WOLFSSL ON)
        set(CURL_USE_OPENSSL OFF)
    elseif(APPLE)
        set(CURL_USE_SECTRANSP ON)
    elseif(WIN32)
        set(CURL_USE_SCHANNEL ON)
    endif()
    add_subdirectory("${CURL_DIR}" EXCLUDE_FROM_ALL)
    target_link_libraries(F95Checker PRIVATE libcurl_static)
else()
    find_package(CURL REQUIRED)
    target_link_libraries(F95Checker PRIVATE CURL::libcurl)
endif()

# bc7e
add_subdirectory("${BC7E_DIR}" EXCLUDE_FROM_ALL)
if(BC7E_AVAILABLE)
    add_dependencies(F95Checker bc7e)
    target_link_libraries(F95Checker PRIVATE bc7e)
    target_compile_definitions(F95Checker PRIVATE BC7E_AVAILABLE=1)
endif()

# shlex
add_subdirectory("${SHLEX_DIR}")
target_link_libraries(F95Checker PRIVATE shlex)

# Build as (almost) static executable
# Adding -static prevents loading OpenGL (or any other) shared libraries at runtime
target_link_libraries(F95Checker PRIVATE -static-libgcc -static-libstdc++)

# Add run targets
add_custom_target(run
    COMMAND ./F95Checker
    DEPENDS F95Checker
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
)
add_custom_target(gdb
    COMMAND gdb -q ./F95Checker
    DEPENDS F95Checker
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
)
