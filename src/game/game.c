#include "game.h"

Game* game_init(void) {
    Game* game = malloc(sizeof(Game));

    m_string_init(game->name);
    m_string_init(game->version);
    m_string_init(game->developer);
    m_string_init(game->url);
    m_string_init(game->last_check_version);
    m_string_init(game->finished);
    m_string_init(game->installed);

    game_executable_list_init(game->executables);

    m_string_init(game->description);
    m_string_init(game->changelog);

    m_bitset_init(game->tags);
    m_bitset_resize(game->tags, 1 + GameTag_COUNT);

    m_string_list_init(game->unknown_tags);

    label_ptr_list_init(game->labels);

    m_string_init(game->notes);
    m_string_init(game->image_url);

    m_string_list_init(game->previews_urls);

    game_download_list_init(game->downloads);

    game_review_list_init(game->reviews);

    game_timeline_event_list_init(game->timeline_events);

    return game;
}

void game_free(Game* game) {
    m_string_clear(game->name);
    m_string_clear(game->version);
    m_string_clear(game->developer);
    m_string_clear(game->url);
    m_string_clear(game->last_check_version);
    m_string_clear(game->finished);
    m_string_clear(game->installed);

    game_executable_list_clear(game->executables);

    m_string_clear(game->description);
    m_string_clear(game->changelog);

    m_bitset_clear(game->tags);

    m_string_list_clear(game->unknown_tags);

    label_ptr_list_clear(game->labels);

    m_string_clear(game->notes);
    m_string_clear(game->image_url);

    m_string_list_clear(game->previews_urls);

    game_download_list_clear(game->downloads);

    game_review_list_clear(game->reviews);

    game_timeline_event_list_clear(game->timeline_events);

    free(game);
}
