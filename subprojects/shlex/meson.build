project('shlex', 'cpp')

source_dir = meson.current_source_dir()
build_dir = meson.current_build_dir()
include_dirs = include_directories('.')
compile_args = [
    '-I' + (source_dir / '..'),
]

sources = ['shlex.cpp', 'shlex.h']
headgen = []
shlexcpp_sources = ['shlex_cpp/shlex.cpp', 'shlex_cpp/shlex.h']

shlex = static_library(
    'shlex', sources + shlexcpp_sources,
    include_directories: include_dirs,
    cpp_args: compile_args,
)

shlex_dep = declare_dependency(
    link_with: shlex,
    sources: headgen,
    include_directories: include_dirs,
    compile_args: compile_args,
)
