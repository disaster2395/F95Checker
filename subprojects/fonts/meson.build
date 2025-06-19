project('fonts', 'c', meson_version: '>=1.1.0')
fs = import('fs')

glob = find_program('meson-glob')
dcimgui_font_gen = find_program('dcimgui_font_gen')
python_exe = find_program('python3-maybe-venv')

source_dir = meson.current_source_dir()
build_dir = meson.current_build_dir()
include_dirs = include_directories()
compile_args = []

resources_dir = source_dir / '../../resources'
files = run_command(glob, resources_dir, 'fonts/*.?tf', check: true).stdout().split('\n')
sources = []
headgen = []
header = '#pragma once\n\n'

foreach file : files
    symbol = 'font_' + fs.name(file).split('.')[0].underscorify().to_lower()
    sources += custom_target(
        symbol + '.c',
        output: symbol + '.c',
        depend_files: [file],
        command: [
            dcimgui_font_gen,
            '-u8', '-nostatic',
            file,
            symbol,
        ],
        capture: true,
    )
    header += 'extern const unsigned int ' + symbol + '_compressed_size;\n'
    header += 'extern const unsigned char ' + symbol + '_compressed_data[];\n\n'
endforeach

# No way to write files with Meson
run_command(
    python_exe, '-c',
    'import pathlib, sys;'+
    'pathlib.Path(sys.argv[1]).write_text(sys.argv[2]);',
    build_dir / 'fonts.h', header,
    check: true,
)

mdi = run_command(glob, resources_dir, 'fonts/materialdesignicons-webfont.*.?tf', check: true).stdout()
sources += custom_target(
    'mdi.h',
    output: 'mdi.h',
    depend_files: [mdi],
    command: [
        python_exe,
        source_dir / 'mdi.py',
        mdi,
        build_dir / 'mdi.h',
    ],
)

foreach source : sources
    foreach source_output : source.to_list()
        if source_output.full_path().endswith('.h')
            headgen += [source_output]
        endif
    endforeach
endforeach

fonts = static_library(
    'fonts', sources,
    include_directories: include_dirs,
    c_args: compile_args,
)

fonts_dep = declare_dependency(
    link_with: fonts,
    sources: headgen,
    include_directories: include_dirs,
    compile_args: compile_args,
)
