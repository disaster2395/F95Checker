#include "fonts.h"

#include <fonts/fonts.h>

#define ImFontAtlas_AddFontFromEmbeddedTTF(fonts, font_name, font_size, font_config) \
    ImFontAtlas_AddFontFromMemoryCompressedTTF(                                      \
        fonts,                                                                       \
        font_##font_name##_compressed_data,                                          \
        font_##font_name##_compressed_size,                                          \
        font_size,                                                                   \
        &font_config,                                                                \
        NULL);

static const ImFontConfig karla_cfg = {
    .OversampleH = 2,
    .OversampleV = 2,
    .GlyphOffset.y = -0.5f,
    .GlyphRanges = (ImWchar[]){0x1, 0x25ca, 0},
    .GlyphMinAdvanceX = 0.0f,
    .GlyphMaxAdvanceX = FLT_MAX,
    .RasterizerMultiply = 1.0f,
    .RasterizerDensity = 1.0f,
};

static const ImFontConfig jbm_cfg = {
    .OversampleH = 2,
    .OversampleV = 2,
    .GlyphRanges = (ImWchar[]){0x1, 0x2b58, 0},
    .GlyphMinAdvanceX = 0.0f,
    .GlyphMaxAdvanceX = FLT_MAX,
    .RasterizerMultiply = 1.0f,
    .RasterizerDensity = 1.0f,
};

static const ImFontConfig mdi_cfg = {
    .MergeMode = true,
    .GlyphOffset.y = +1.0f,
    .GlyphRanges = (ImWchar[]){mdi_char_min, mdi_char_max, 0},
    .GlyphMinAdvanceX = 0.0f,
    .GlyphMaxAdvanceX = FLT_MAX,
    .RasterizerMultiply = 1.0f,
    .RasterizerDensity = 1.0f,
};

void gui_fonts_init(Gui* gui) {
    ImFontAtlas* f = gui->io->Fonts;

    gui->fonts.base = ImFontAtlas_AddFontFromEmbeddedTTF(f, karla_regular, 18, karla_cfg);
    ImFontAtlas_AddFontFromEmbeddedTTF(f, materialdesignicons_webfont, 18, mdi_cfg);

    gui->fonts.mono = ImFontAtlas_AddFontFromEmbeddedTTF(f, jetbrainsmono_regular, 17, jbm_cfg);

    // FIXME: load missing fonts
}

void gui_fonts_free(Gui* gui) {
    ImFontAtlas_Clear(gui->io->Fonts);
    memset(&gui->fonts, NULL, sizeof(gui->fonts));
}
