#include "backend.h"

#include <dcimgui/backends/dcimgui_impl_opengl3.h>
#include <dcimgui/backends/dcimgui_impl_sdl3.h>
#include <glad/gl.h>

#include <globals.h>

static inline void gui_backend_sdl_perror(const char* s) {
    custom_perror(s, SDL_GetError());
}

bool gui_backend_init(Gui* gui, const char* title, uint32_t width, uint32_t height) {
    // Prefer Wayland when available
    SDL_SetHint(SDL_HINT_VIDEO_DRIVER, "wayland");

    if(!SDL_Init(SDL_INIT_VIDEO)) {
        gui_backend_sdl_perror("SDL_Init()");

        if(strcmp(SDL_GetError(), "wayland not available") == 0) {
            SDL_ResetHint(SDL_HINT_VIDEO_DRIVER);
            if(!SDL_Init(SDL_INIT_VIDEO)) {
                gui_backend_sdl_perror("SDL_Init()");
                return false;
            }
        } else {
            return false;
        }
    }

    // From 2.0.18: Enable native IME.
#ifdef SDL_HINT_IME_SHOW_UI
    SDL_SetHint(SDL_HINT_IME_SHOW_UI, "1");
#endif

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24);
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 0);
    const SDL_WindowFlags window_flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE |
                                         SDL_WINDOW_HIGH_PIXEL_DENSITY;
    gui->window = SDL_CreateWindow(title, width, height, window_flags);
    if(gui->window == NULL) {
        gui_backend_sdl_perror("SDL_CreateWindow()");
        return false;
    }
    SDL_SetWindowMinimumSize(gui->window, 720, 400);

    gui->gl = SDL_GL_CreateContext(gui->window);
    SDL_GL_MakeCurrent(gui->window, gui->gl);
    SDL_GL_SetSwapInterval(1);

    const int32_t version = gladLoadGL(SDL_GL_GetProcAddress);
    if(version == 0) {
        custom_perror("gladLoadGL()", "failed to initialize OpenGL context");
        SDL_GL_DestroyContext(gui->gl);
        SDL_DestroyWindow(gui->window);
        SDL_Quit();
        return false;
    }

    IMGUI_CHECKVERSION();
    ImGui_CreateContext(NULL);
    gui->io = ImGui_GetIO();
    gui->style = ImGui_GetStyle();
    gui->prev_size = (ImVec2){0.0f, 0.0f};
    gui->scroll_energy = (ImVec2){0.0f, 0.0f};

    ImGui_ImplSDL3_InitForOpenGL(gui->window, gui->gl);
    ImGui_ImplOpenGL3_Init();

    return true;
}

void gui_backend_process_events(Gui* gui) {
    SDL_Event event;
    bool requested_close = false;
    while(SDL_PollEvent(&event)) {
        if(event.type == SDL_EVENT_MOUSE_WHEEL &&
           event.window.windowID == SDL_GetWindowID(gui->window)) {
            // Handle wheel events locally to apply smooth scrolling
            event.wheel.x *= settings->scroll_amount;
            event.wheel.y *= settings->scroll_amount;
            if(settings->scroll_smooth) {
                // Immediately stop if direction changes
                if(gui->scroll_energy.x * event.wheel.x < 0.0f) {
                    gui->scroll_energy.x = 0.0f;
                }
                if(gui->scroll_energy.y * event.wheel.y < 0.0f) {
                    gui->scroll_energy.y = 0.0f;
                }
            }
            gui->scroll_energy.x += event.wheel.x;
            gui->scroll_energy.y += event.wheel.y;
        } else {
            ImGui_ImplSDL3_ProcessEvent(&event);
        }

        // QUIT is sent after WINDOW_CLOSE_REQUESTED for window closing
        // Only QUIT is sent when trying to terminate the process
        // For terminating process, close right away
        // For window close, register request and handle later
        if(event.type == SDL_EVENT_QUIT) {
            if(!requested_close) {
                gui->should_close = true;
            }
        }
        if(event.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED &&
           event.window.windowID == SDL_GetWindowID(gui->window)) {
            requested_close = true;
        }
    }

    // FIXME: change behavior based on settings, implement tray icon
    // If window close was requested, save it and handle in draw in case confirmation is needed
    // If requested a second time, just close anyway
    if(requested_close) {
        if(gui->requested_close) {
            gui->should_close = true;
        } else {
            gui->requested_close = true;
        }
    }
}

void gui_backend_new_frame(Gui* gui) {
    UNUSED(gui);

    // Apply smooth scrolling
    ImVec2 scroll_now;
    if(settings->scroll_smooth) {
        if(ABS(gui->scroll_energy.x) > 0.01f) {
            scroll_now.x =
                gui->scroll_energy.x * gui->io->DeltaTime * settings->scroll_smooth_speed;
            gui->scroll_energy.x -= scroll_now.x;
        } else {
            // Cutoff smoothing when it's basically stopped
            scroll_now.x = 0.0f;
            gui->scroll_energy.x = 0.0f;
        }
        if(ABS(gui->scroll_energy.y) > 0.01f) {
            scroll_now.y =
                gui->scroll_energy.y * gui->io->DeltaTime * settings->scroll_smooth_speed;
            gui->scroll_energy.y -= scroll_now.y;
        } else {
            // Cutoff smoothing when it's basically stopped
            scroll_now.y = 0.0f;
            gui->scroll_energy.y = 0.0f;
        }
    } else {
        scroll_now = gui->scroll_energy;
        gui->scroll_energy = (ImVec2){0, 0};
    }
    gui->io->MouseWheel = scroll_now.y;
    gui->io->MouseWheelH = -scroll_now.x;

    // Hand cursor when hovering buttons and similar
    if(ImGui_IsAnyItemHovered()) {
        ImGui_SetMouseCursor(ImGuiMouseCursor_Hand);
    }

    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplSDL3_NewFrame();
    ImGui_NewFrame();
}

void gui_backend_render(Gui* gui) {
    ImGui_Render();
    glViewport(0, 0, (int32_t)gui->io->DisplaySize.x, (int32_t)gui->io->DisplaySize.y);
    ImGui_ImplOpenGL3_RenderDrawData(ImGui_GetDrawData());
    SDL_GL_SwapWindow(gui->window);
}

void gui_backend_free(Gui* gui) {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplSDL3_Shutdown();
    ImGui_DestroyContext(NULL);

    SDL_GL_DestroyContext(gui->gl);
    SDL_DestroyWindow(gui->window);
    SDL_Quit();
}
