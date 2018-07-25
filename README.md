Allows the usage of regular expressions as triggers for bot responses

Regular expressions and their responses are stored in a seperate file which can be opened in the systems default editor by pressing the edit button

## File Format

A regex must be encapsulated by forward slashes. The response must be encapsulated by double quotation marks.

One line per regex/response pair

`<regex> [<cooldown> [<permission> <special permission>]] <response>`

Explanation:

`<regex>` **(must be present)** The regular expression that should be matched surrounded by front slashes / and must be on continuous string without whitespaces.

`<cooldown>` If present, the cooldown for that regex match in seconds. 0 for no cooldown.

`<permission>` If present, the user class that can trigger this regex match. Same classes possible as in the bot: `everyone`, `moderator`, `subscriber`, `user_specific`, `editor`

`<special permission>` Must be present if `<permission>` is `user_specific`. Comma seperated list of usernames allowed to trigger this regex match.

`<response>` **(must be present)** The response that will be send to chat if the regex matches a chat message (or part of it). Must be surrounded by ". Nested " are allowed.

Available paramters are:

`$username` - Name of the user who triggered the regex

`$message` - The full message the regex was found in

### Examples

WOW bot example. Uses default settings from the bot's UI

`/.*[wW].*[oO].*[wW].*/ "WOW ConcernDoge"`

This can be used for moderation as well.

`/\(\s*\.\s*([yY]|\)\s*\()\s*\.\s*\)/ 0 everyone "/timeout $username 600 rekt by regex for $message"`

More infos on regular expressoins: https://docs.python.org/2/library/re.html

Test your regex's here: https://regexr.com/