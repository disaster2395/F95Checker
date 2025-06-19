#include "shlex.h"

#include <shlex_cpp/shlex.h>

void shlex_split(const char* command_line, m_string_list_ptr args_list) {
    std::string cpp_command_line = command_line;
    std::vector<std::string> cpp_args_list;
    try {
        cpp_args_list = shlex::split(cpp_command_line);
    } catch(std::runtime_error&) {
        return;
    }

    m_string_t c_arg;
    m_string_init(c_arg);
    for(std::string cpp_arg : cpp_args_list) {
        m_string_set_cstr(c_arg, cpp_arg.c_str());
        m_string_list_push_back(args_list, c_arg);
    }
    m_string_clear(c_arg);
}

void shlex_join(m_string_list_ptr args_list, m_string_ptr command_line) {
    bool first_arg = true;
    for each(m_string_ptr, c_arg, m_string_list_t, args_list) {
        if(first_arg) {
            first_arg = false;
        } else {
            m_string_push_back(command_line, ' ');
        }

        std::string cpp_arg = m_string_get_cstr(c_arg);
        std::string cpp_arg_quoted = shlex::quote(cpp_arg);
        m_string_cat_cstr(command_line, cpp_arg_quoted.c_str());
    }
}
