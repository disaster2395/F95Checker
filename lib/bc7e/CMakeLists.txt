find_program(ISPC_FOUND ispc)
if(ISPC_FOUND)
    set(BC7E_SRC "${BC7E_GEN}/bc7e.ispc")
    set(BC7E_OBJ "${CMAKE_CURRENT_BINARY_DIR}/bc7e.o")
    set(BC7E_H "${CMAKE_CURRENT_SOURCE_DIR}/bc7e.h")
    file(RELATIVE_PATH BC7E_H_REL "${PROJECT_SOURCE_DIR}" "${BC7E_H}")
    set(BC7E_OBJS "${BC7E_OBJ}")
    set(BC7E_HS "${BC7E_H}")
    set(BC7E_TARGETS sse2 sse4 avx avx2)
    foreach(target IN LISTS BC7E_TARGETS)
        list(APPEND BC7E_OBJS "${CMAKE_CURRENT_BINARY_DIR}/bc7e_${target}.o")
        list(APPEND BC7E_HS "${CMAKE_CURRENT_SOURCE_DIR}/bc7e_${target}.h")
    endforeach()
    list(JOIN BC7E_TARGETS "," BC7E_TARGET)
    add_custom_command(
        OUTPUT ${BC7E_OBJS} ${BC7E_HS}
        COMMAND ispc --PIC -g -O2 --woff --target=${BC7E_TARGET} --opt=fast-math --opt=disable-assertions "${BC7E_SRC}" -o "${BC7E_OBJ}" -h "${BC7E_H_REL}"
        DEPENDS "${BC7E_SRC}"
        COMMENT "Building ISPC library bc7e"
        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    )
    add_library(bc7e STATIC "${BC7E_OBJS}")
    SET_TARGET_PROPERTIES(bc7e PROPERTIES LINKER_LANGUAGE C)
    set(BC7E_AVAILABLE ON PARENT_SCOPE)
else()
    message(WARNING "ISPC not found, continuing without BC7 support!")
    set(BC7E_AVAILABLE OFF PARENT_SCOPE)
endif()
