project('sqlite3', 'c')

source_dir = meson.current_source_dir()
build_dir = meson.current_build_dir()
include_dirs = include_directories('.')
compile_args = [
    # https://sqlite.org/compile.html#recommended_compile_time_options
    '-DSQLITE_DQS=0',
    '-DSQLITE_THREADSAFE=0',
    '-DSQLITE_DEFAULT_MEMSTATUS=0',
    '-DSQLITE_DEFAULT_WAL_SYNCHRONOUS=1',
    '-DSQLITE_LIKE_DOESNT_MATCH_BLOBS',
    '-DSQLITE_MAX_EXPR_DEPTH=0',
    '-DSQLITE_OMIT_DEPRECATED',
    '-DSQLITE_OMIT_PROGRESS_CALLBACK',
    '-DSQLITE_OMIT_SHARED_CACHE',
    '-DSQLITE_USE_ALLOCA',
    '-DSQLITE_OMIT_AUTOINIT',
    '-DSQLITE_STRICT_SUBTYPE=1',
]

sources = ['sqlite3.c', 'sqlite3.h', 'sqlite3ext.h']
headgen = []

sqlite3 = static_library(
    'sqlite3', sources,
    include_directories: include_dirs,
    c_args: compile_args,
)

sqlite3_dep = declare_dependency(
    link_with: sqlite3,
    sources: headgen,
    include_directories: include_dirs,
    compile_args: compile_args,
)
