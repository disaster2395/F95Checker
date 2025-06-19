#pragma once

#include <std.h>

#ifdef __cplusplus
extern "C" {
#endif

void shlex_split(const char* command_line, m_string_list_ptr args_list);

void shlex_join(m_string_list_ptr args_list, m_string_ptr command_line);

#ifdef __cplusplus
}
#endif
