#include "window.h"

#include <dcimgui/backends/dcimgui_impl_opengl3.h>
#include <dcimgui/backends/dcimgui_impl_sdl3.h>
#include <glad/gl.h>

#include <globals.h>

bool gui_window_init(Gui* gui) {
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24);
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 0);
    const SDL_WindowFlags window_flags = SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE |
                                         SDL_WINDOW_HIDDEN | SDL_WINDOW_HIGH_PIXEL_DENSITY;
    // FIXME: load and save window size from imgui.ini
    // FIXME: use data path for imgui.ini
    gui->window = SDL_CreateWindow("F95Checker WIP C Rewrite", 1280, 720, window_flags);
    if(gui->window == NULL) {
        gui_perror("SDL_CreateWindow()");
        return false;
    }
    SDL_SetWindowMinimumSize(gui->window, 720, 400);
    SDL_SetWindowIcon(gui->window, gui->icons.icon);

    gui->window_gl = SDL_GL_CreateContext(gui->window);
    SDL_GL_MakeCurrent(gui->window, gui->window_gl);
    SDL_GL_SetSwapInterval(1);

    const int32_t version = gladLoadGL(SDL_GL_GetProcAddress);
    if(version == 0) {
        custom_perror("gladLoadGL()", "failed to initialize OpenGL context");
        SDL_GL_DestroyContext(gui->window_gl);
        SDL_DestroyWindow(gui->window);
        SDL_Quit();
        return false;
    }

    IMGUI_CHECKVERSION();
    ImGui_CreateContext(NULL);
    gui->io = ImGui_GetIO();
    gui->style = ImGui_GetStyle();
    gui->window_state.prev_size = (ImVec2){0.0f, 0.0f};
    gui->window_state.scroll_energy = (ImVec2){0.0f, 0.0f};

    ImGui_ImplSDL3_InitForOpenGL(gui->window, gui->window_gl);
    ImGui_ImplOpenGL3_Init();

    return true;
}

void gui_window_process_event(Gui* gui, SDL_Event* event) {
    if(event->type == SDL_EVENT_MOUSE_WHEEL &&
       event->window.windowID == SDL_GetWindowID(gui->window)) {
        // Handle wheel events locally to apply scroll settings
        event->wheel.x *= settings->scroll_amount;
        event->wheel.y *= settings->scroll_amount;
        if(settings->scroll_smooth) {
            // Immediately stop if direction changes
            if(gui->window_state.scroll_energy.x * event->wheel.x < 0.0f) {
                gui->window_state.scroll_energy.x = 0.0f;
            }
            if(gui->window_state.scroll_energy.y * event->wheel.y < 0.0f) {
                gui->window_state.scroll_energy.y = 0.0f;
            }
        }
        gui->window_state.scroll_energy.x += event->wheel.x;
        gui->window_state.scroll_energy.y += event->wheel.y;
    } else {
        ImGui_ImplSDL3_ProcessEvent(event);
    }
}

void gui_window_new_frame(Gui* gui) {
    UNUSED(gui);

    // Apply smooth scrolling
    ImVec2 scroll_now;
    if(settings->scroll_smooth) {
        if(ABS(gui->window_state.scroll_energy.x) > 0.01f) {
            scroll_now.x = gui->window_state.scroll_energy.x * gui->io->DeltaTime *
                           settings->scroll_smooth_speed;
            gui->window_state.scroll_energy.x -= scroll_now.x;
        } else {
            // Cutoff smoothing when it's basically stopped
            scroll_now.x = 0.0f;
            gui->window_state.scroll_energy.x = 0.0f;
        }
        if(ABS(gui->window_state.scroll_energy.y) > 0.01f) {
            scroll_now.y = gui->window_state.scroll_energy.y * gui->io->DeltaTime *
                           settings->scroll_smooth_speed;
            gui->window_state.scroll_energy.y -= scroll_now.y;
        } else {
            // Cutoff smoothing when it's basically stopped
            scroll_now.y = 0.0f;
            gui->window_state.scroll_energy.y = 0.0f;
        }
    } else {
        scroll_now = gui->window_state.scroll_energy;
        gui->window_state.scroll_energy = (ImVec2){0, 0};
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

    ImGui_SetNextWindowPos((ImVec2){0.0f, 0.0f}, ImGuiCond_Once);
    int32_t width, height;
    SDL_GetWindowSize(gui->window, &width, &height);
    const ImVec2 window_size = {width, height};
    if(window_size.x != gui->window_state.prev_size.x ||
       window_size.y != gui->window_state.prev_size.y) {
        ImGui_SetNextWindowSize(window_size, ImGuiCond_Always);
    }

    ImGui_PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
    ImGui_Begin(
        "F95Checker",
        NULL,
        ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse |
            ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoScrollbar |
            ImGuiWindowFlags_NoScrollWithMouse);
    ImGui_PopStyleVar();
}

void gui_window_render(Gui* gui) {
    ImGui_End();

    ImGui_Render();
    glViewport(0, 0, (int32_t)gui->io->DisplaySize.x, (int32_t)gui->io->DisplaySize.y);
    ImGui_ImplOpenGL3_RenderDrawData(ImGui_GetDrawData());
    SDL_GL_SwapWindow(gui->window);
}

void gui_window_free(Gui* gui) {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplSDL3_Shutdown();
    ImGui_DestroyContext(NULL);

    SDL_GL_DestroyContext(gui->window_gl);
    SDL_DestroyWindow(gui->window);
}
