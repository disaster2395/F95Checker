project('icons', 'c', meson_version: '>=1.1.0')
fs = import('fs')

glob = find_program('meson-glob')
python_exe = find_program('python3-maybe-venv')

source_dir = meson.current_source_dir()
build_dir = meson.current_build_dir()
include_dirs = include_directories()
compile_args = []

resources_dir = source_dir / '../../resources'
files = run_command(glob, resources_dir, 'icons/*.png', check: true).stdout().split('\n')
sources = []
headgen = []
header = '#pragma once\n\n'

foreach file : files
    symbol = 'icon_' + fs.name(file).split('.')[0].underscorify().to_lower()
    sources += custom_target(
        symbol + '.c',
        output: symbol + '.c',
        depend_files: [file],
        command: [
            python_exe,
            source_dir / 'icon.py',
            file,
            symbol,
            build_dir / symbol + '.c',
        ],
    )
    header += 'extern const unsigned int ' + symbol + '_width;\n'
    header += 'extern const unsigned int ' + symbol + '_height;\n'
    header += 'extern const unsigned char ' + symbol + '_pixels[];\n\n'
endforeach

# No way to write files with Meson
run_command(
    python_exe, '-c',
    'import pathlib, sys;'+
    'pathlib.Path(sys.argv[1]).write_text(sys.argv[2]);',
    build_dir / 'icons.h', header,
    check: true,
)

icons = static_library(
    'icons', sources,
    include_directories: include_dirs,
    c_args: compile_args,
)

icons_dep = declare_dependency(
    link_with: icons,
    sources: headgen,
    include_directories: include_dirs,
    compile_args: compile_args,
)
