#pragma once

#include "browser/browser.h"
#include "db/db.h"
#include "game/game.h"
#include "gui/gui.h"
#include "settings/settings.h"
#include "types/cookie.h"
#include "types/label.h"
#include "types/tab.h"

extern Os os;
extern BrowserList browsers;
extern Db* db;
extern GameDict games;
extern Gui* gui;
extern Settings* settings;
extern CookieDict cookies;
extern LabelList labels;
extern TabList tabs;
