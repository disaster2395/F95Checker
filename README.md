# F95CheckerX

If you never used F95Checker before, please read [original README](https://github.com/Willy-JL/F95Checker).

This document only mentions parts that were changed or added.

Also, please read the [DISCLAIMER](https://github.com/littleraisins/F95CheckerX#warning-disclaimer) before using this version.

:arrow_down: **[Download](https://github.com/littleraisins/F95CheckerX/releases/latest)**

## :dna: Modifications:

- **Reminders**: Separate games you love and games that you want to keep an eye on.
- **Powerful filtering**: Save different sets of filters, support for OR queries, and autocomplete.
- **Multiple images per thread**: Add your own screenshots or automatically download thread attachments.

And more miscellaneous stuff missing from the original:
  - Various browser addon improvements and bug fixes (PR pending https://github.com/Willy-JL/F95Checker/pull/90)
  - Filter by developer + quick filter by clicking dev name (https://github.com/Willy-JL/F95Checker/issues/54).
  - Dedicated "Custom game" filter (https://github.com/Willy-JL/F95Checker/issues/88).

## :link: Browser addon

> **IMPORTANT**: The original browser addon (red icon) won't work with this version!  
> But, you can safely install both browser addons, and run them at the same time.

- **Firefox:** Install from [Mozilla Addons](https://addons.mozilla.org/en-US/firefox/addon/f95checkerx-browser-addon/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

- **Chrome:** Open `chrome://extensions`, enable "Developer mode", drag and drop `extension/chrome.zip`
  
## :card_file_box: Data locations:

  - `%APPDATA%\f95checkerx\` on Windows
    (usually `C:\Users\username\AppData\Roaming\f95checkerx\`)
  - `~/.config/f95checkerx/` on Linux
    (usually `/home/username/.config/f95checkerx/`)
  - `~/Library/Application Support/f95checkerx/` on MacOS
    (usually `/Users/username/Library/Application Support/f95checkerx/`)

## :warning: Disclaimer:

- You can safely install both browser addons, and run them at the same time.
- This version will receive updates and bugfixes from F95Checker original repo.
- If you are migrating from F95Checker just copy your database file to `f95checkerx` directory.
- The only way to switch back to regular version is to export+import threads, database is not compatible.
- If you are using F95CheckerX report all issues to this repo, I will forward them to F95Checker if necessary.
- F95CheckerX creates folders separate from your F95Checker installation to avoid any conflicts and loss of data.
- Treat every release of F95CheckerX as beta, if you want stable version get latest release of F95Checker [here](https://github.com/Willy-JL/F95Checker/releases/latest)
