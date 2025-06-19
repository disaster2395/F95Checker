// Remove imgui.h defines before dcimgui.h re-defines them
#undef IMGUI_CHECKVERSION
#undef IM_ALLOC
#undef IM_FREE

// 32-bit characters for drawing
#define IMGUI_USE_WCHAR32 1

// Max amount of items for ListClipper before 32bit int coordinates cause issues
#define IMGUI_LISTCLIPPER_MAX 1'000'000

// Define OPLIST for use with M*LIB types
#define M_OPL_ImColor() M_POD_OPLIST
