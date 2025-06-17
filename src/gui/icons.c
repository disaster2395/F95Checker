#include "icons.h"

#include <icons/icons.h>

// TODO: maybe this should be done differently, storing uncompressed RGBA in the binary takes ~9MB currently

#define SDL_CreateSurfaceFromEmbeddedIcon(icon_name) \
    SDL_CreateSurfaceFrom(                           \
        icon_##icon_name##_width,                    \
        icon_##icon_name##_height,                   \
        SDL_PIXELFORMAT_RGBA32,                      \
        (void*)icon_##icon_name##_pixels,            \
        icon_##icon_name##_width * 4);

void gui_icons_init(Gui* gui) {
    gui->icons.icon = SDL_CreateSurfaceFromEmbeddedIcon(icon);
    gui->icons.logo = SDL_CreateSurfaceFromEmbeddedIcon(logo);
    gui->icons.paused = SDL_CreateSurfaceFromEmbeddedIcon(paused);
    gui->icons.refreshing[0] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing1);
    gui->icons.refreshing[1] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing2);
    gui->icons.refreshing[2] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing3);
    gui->icons.refreshing[3] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing4);
    gui->icons.refreshing[4] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing5);
    gui->icons.refreshing[5] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing6);
    gui->icons.refreshing[6] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing7);
    gui->icons.refreshing[7] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing8);
    gui->icons.refreshing[8] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing9);
    gui->icons.refreshing[9] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing10);
    gui->icons.refreshing[10] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing11);
    gui->icons.refreshing[11] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing12);
    gui->icons.refreshing[12] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing13);
    gui->icons.refreshing[13] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing14);
    gui->icons.refreshing[14] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing15);
    gui->icons.refreshing[15] = SDL_CreateSurfaceFromEmbeddedIcon(refreshing16);
}

void gui_icons_free(Gui* gui) {
    SDL_DestroySurface(gui->icons.icon);
    SDL_DestroySurface(gui->icons.logo);
    SDL_DestroySurface(gui->icons.paused);
    for(size_t i = 0; i < COUNT_OF(gui->icons.refreshing); i++) {
        SDL_DestroySurface(gui->icons.refreshing[i]);
    }
}
