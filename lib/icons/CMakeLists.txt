# Find icons
file(GLOB icons "${RESOURCES_DIR}/icons/*.png")
set(sources)
set(header "#pragma once\n\n")

# Process icons
foreach(icon_src IN LISTS icons)
    get_filename_component(icon_name "${icon_src}" NAME_WE)
    string(REGEX REPLACE "[^A-Za-z0-9_]" "_" icon_symbol "${icon_name}")
    string(TOLOWER "${icon_symbol}" icon_symbol)
    set(icon_symbol "icon_${icon_symbol}")
    set(icon_dst "${ICONS_DIR}/${icon_symbol}.c")
    # Generate binaries
    file(RELATIVE_PATH icon_src_rel "${PROJECT_SOURCE_DIR}" "${icon_src}")
    add_custom_command(
        OUTPUT "${icon_dst}"
        COMMAND "${Python_EXECUTABLE}" "${ICONS_DIR}/icon.py" "${icon_src_rel}" "${icon_symbol}" "${icon_dst}"
        DEPENDS "${ICONS_DIR}/icon.py" "${icon_src}"
        COMMENT "Generating embedded icon ${icon_name}"
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    )
    # Append declaration
    string(CONCAT header "${header}" "extern const unsigned int ${icon_symbol}_width;\n")
    string(CONCAT header "${header}" "extern const unsigned int ${icon_symbol}_height;\n")
    string(CONCAT header "${header}" "extern const unsigned char ${icon_symbol}_pixels[];\n\n")
    # Add sources
    list(APPEND sources "${icon_dst}")
endforeach()

# Write generated header
file(WRITE "${ICONS_DIR}/icons.h" "${header}")
list(APPEND sources "${ICONS_DIR}/icons.h")

# Build as static library
add_library(icons STATIC "${sources}")

# Include paths to use and propagate
target_include_directories(icons PUBLIC "${ICONS_DIR}")
