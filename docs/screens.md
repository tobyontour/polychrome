Screens
=======

Login
-----

Username and password form. If login works then go to main menu or read messages
if there are any unread messages.

### Metadata

* Add to stack: No
* Goes to:
  * Message of the day (if there are any unread system messages)
  * Read messages (if there are any unread messages)
  * Main menu

Menu
----

### Contents

* Header text - up to N lines.
* Horizontal rule containing menu owner and keypath
* List of menu options with:
  * title
  * key press
  * Type (Add, Menu, Run)
  * Last change date for files
  * unread indicator + or - (or = for menu)
  * owner (in brackets) if not the menu owner
* Footer options:
  * Back
  * Scan
  * Options
  * Help

### Meta data

* Add to stack: Yes
* Goes to:
  * File viewer
  * Run
  * Utilities

File viewer
-----------

Displays a list of posts in a file.

### Contents

* Header text for file.
* Horizontal rule
* list of posts:
  * Horizontal rule containing date
  * From line containing username and nameline
  * Blank line
  * Subject line
  * Rest of content
* Footer options:
  * More [space]
  * Exit (pop) [q]
  * Send reply [s]
  * Add [a]
  * Help [?]
  * Percentage display.


### Metadata

* Add to stack: Yes
* Goes to:
  * Compose message (forward)
  * Compose post
  * Back (pop)


