import os
import pathlib
import sys


def mod_version(original_version) -> str:
    version_parts = original_version.split(".")
    while len(version_parts) < 3:
        version_parts.append("0")
    version_parts[2] = str(int(version_parts[2]) + 1)
    return ".".join(version_parts)


version = "11.1"
version = mod_version(version)
release = False
build_number = 0
version_name = f"{version}{'' if release else ' beta'}{'' if release or not build_number else ' ' + str(build_number)} (b-mod)"
rpc_port = 57095
rpc_url = f"http://127.0.0.1:{rpc_port}"

frozen = getattr(sys, "frozen", False)
self_path = (pathlib.Path(sys.executable) if frozen else pathlib.Path(__file__).parent).parent
debug = not (frozen or release)
if not sys.stdout or not sys.stderr or os.devnull in (sys.stdout.name, sys.stderr.name):
    debug = False

if "F95DEBUG" not in os.environ:
    os.environ["F95DEBUG"] = str(int(debug))
