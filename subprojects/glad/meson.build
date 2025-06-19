project('glad', 'c')

python_exe = find_program('python3-maybe-venv')

source_dir = meson.current_source_dir()
build_dir = meson.current_build_dir()
include_dirs = include_directories()
compile_args = [
    '-I' + (build_dir / 'include'),
]

api = 'gl:core=3.0'
sources = []
headgen = []

sources += custom_target(
    'gl.c',
    output: ['gl.c', 'gl.h', 'khrplatform.h'],
    command: [
        # GLAD outputs in subfolders (src/gl.c, include/glad/gl.h, include/KHR/khrplatform.h)
        # Meson is picky and *only* allows outputs directly in the build dir with custom_target()
        # So wrap it with python and move the files to please Meson
        python_exe, '-c',
        'import os, pathlib, shutil, subprocess, sys;'+
        'glad = pathlib.Path(sys.argv[1]);'+
        'subprocess.run(sys.argv[2:]);'+
        '(glad / "src/gl.c").rename(glad / "gl.c");'+
        '(glad / "src").rmdir();',
        build_dir,
        # Actual command here
        python_exe,
        '-m', 'glad',
        '--api', api,
        '--quiet', '--merge',
        '--out-path', build_dir,
        'c',
    ],
)

foreach source : sources
    foreach source_output : source.to_list()
        if source_output.full_path().endswith('.h')
            headgen += [source_output]
        endif
    endforeach
endforeach

glad = static_library(
    'glad', sources,
    include_directories: include_dirs,
    c_args: compile_args,
)

glad_dep = declare_dependency(
    link_with: glad,
    sources: headgen,
    include_directories: include_dirs,
    compile_args: compile_args,
)
