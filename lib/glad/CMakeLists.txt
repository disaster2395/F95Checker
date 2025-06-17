set(glad_sources "${GLAD_DIR}/src/gl.c" "${GLAD_DIR}/include/glad/gl.h" "${GLAD_DIR}/include/KHR/khrplatform.h")

# Generate bindings
add_custom_command(
    OUTPUT ${glad_sources}
    COMMAND "${Python_EXECUTABLE}" -m glad --api gl:core=3.0 --quiet --merge --out-path "${GLAD_DIR}" --reproducible c
    COMMENT "Generating OpenGL dynamic bindings with GLAD"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
)

# Build as static library
add_library(glad STATIC "${glad_sources}")

# Include paths to use and propagate
target_include_directories(glad PUBLIC "${GLAD_DIR}/include")
