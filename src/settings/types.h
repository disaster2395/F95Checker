#pragma once

#include <dcimgui/dcimgui.h>
#include <smart_enum/smart_enum.h>

#include <std.h>

#define _DisplayMode(_, $) \
    _($, List, 1)          \
    _($, Grid, 2)          \
    _($, Kanban, 3)
SMARTENUM_DECLARE(_DisplayMode, DisplayMode)
typedef struct {
    const char* icon;
} DisplayModeInfo;
extern const DisplayModeInfo display_mode[1 + DisplayMode_COUNT];

#define _Os(_, $)    \
    _($, Windows, 1) \
    _($, Linux, 2)   \
    _($, MacOS, 3)
SMARTENUM_DECLARE(_Os, Os)

#define _ProxyType(_, $) \
    _($, Disabled, 1)    \
    _($, SOCKS4, 2)      \
    _($, SOCKS5, 3)      \
    _($, HTTP, 4)
SMARTENUM_DECLARE(_ProxyType, ProxyType)

#define _TagHighlight(_, $) \
    _($, None, 0)           \
    _($, Positive, 1)       \
    _($, Negative, 2)       \
    _($, Critical, 3)
SMARTENUM_DECLARE(_TagHighlight, TagHighlight)
typedef struct {
    ImColor color;
} TagHighlightInfo;
extern const TagHighlightInfo tag_highlight[TagHighlight_COUNT];

#define _TexCompress(_, $) \
    _($, Disabled, 1)      \
    _($, ASTC, 2)          \
    _($, BC7, 3)
SMARTENUM_DECLARE(_TexCompress, TexCompress)

#define _TimelineEventType(_, $)          \
    _($, GameAdded, 1)                    \
    _($, GameLaunched, 2)                 \
    _($, GameFinished, 3)                 \
    _($, GameInstalled, 4)                \
    _($, ChangedName, 5)                  \
    _($, ChangedStatus, 6)                \
    _($, ChangedVersion, 7)               \
    _($, ChangedDeveloper, 8)             \
    _($, ChangedType, 9)                  \
    _($, TagsAdded, 10)                   \
    _($, TagsRemoved, 11)                 \
    _($, ScoreIncreased, 12)              \
    _($, ScoreDecreased, 13)              \
    _($, RecheckExpired, 14) /* Unused */ \
    _($, RecheckUserReq, 15)
SMARTENUM_DECLARE(_TimelineEventType, TimelineEventType)
typedef struct {
    const char* display;
    const char* icon;
    uint8_t args_min;
    const char* template;
} TimelineEventTypeInfo;
extern const TimelineEventTypeInfo timeline_event_type[1 + TimelineEventType_COUNT];
