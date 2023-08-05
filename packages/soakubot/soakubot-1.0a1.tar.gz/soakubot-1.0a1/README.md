# OM-Bot
Bot for OverMobile games from 2014-2015 like mrush, tiwar... **Please don't use without my permission**.

- Partially secured from "CLICKING TOO FAST" annoying message; only work on the Polish server - support for other sites is welcome.
- Secured from `user-agent` checking.

>This API is yet a work in progress. It is missing *a lot* of features. 
>I also have a JS API for this, which is incomplete too, but has more features.
>However, I'm no longer improving it, since that was a very bad implementation.
>It also consumed so much RAM that it ended in a BSoD twice for me.

## Installation

    pip install soakubot

## Connecting

```python
import sb

s = sb.connect("nickname", "password", "site, ex. 'http://mrush.net'")
```

### Global properties

Every object has the properties below:

- `nick` - User nick
- `site` - Website address given on initialization
- `session` - [Requests](//github.com/requests/requests) session

## `forum` object

API for getting data about a forum category.

Usage:

```python
forumid = 1
forum = s.forum(forumid)
```

### Properties

- `id` - Forum ID
- + global properties

### Methods

- `thread(name, msg)` - Creates a thread in the category. Returns a [**thread** object](#thread-object).
- `scan(page=1)` - Scan the forum for threads starting at the given page, ending on the last. Returns an **array** of [thread objects](#thread-object)

## `thread` object

API for getting data about a forum thread.

Usage:

```python
threadid = 1
thread = s.thread(threadid)
```

### Properties

- `id` - Thread ID
- `msg` - Thread message. *Don't trust this one.*
- + global properties

### Methods

- `list(html)` - Parses thread HTML and reads all posts data, including post ID, text (no emotes/bbc), html, author id and his nick. **Used by the `read` method, not expected to use alone.**
- `read()` - Reads two last pages of the thread and returns an array of [post objects](#post-object)
- `reply(msg, to=0)` - Reply to the thread. To send a notification to the reciever, put his ID in the `to` attribute.
- `open()` - Open thread
- `close()` - Close thread
- `pin()` - Pin thread
- `unpin()` - Unpin thread
- `edit(name, msg=Unknown(), insert=None)` - Edit thread title, optionally message. Use the `insert` argument to insert the message at specific postion to decrease data usage. (ex `-1` to append to the thread)

## `post` object

API for getting data about a forum post.

Usage:

```python
postid = 1
post = s.post(postid)
```

### Properties

- `id` - Post ID
- `text` - Post text
- `html` - Post HTML
- `bbc` - Post BBC *Don't trust this one*
- `author` - Dict containing two properties: `id` and `nick`

### Methods

- `get_bbcode` - Doesn't do anything yet. **TODO:** make it useful.

## `private` object

API for managing private messenges.

Usage:

```python
userid = 1
pm = s.private(userid)
```

Doesn't work yet. **TODO:** Make it useful

# TODO's

- [Post](#post-object)'s `get_bbcode`
- [Private object](#private-object)
- Clan object
  - Reading history
  - It's name (both with and without crest)
- Chat object
  - Reading chat messages
  - Replying in chat
  - Deleting messages
- Image library *static* object
  - Library to all available images, using simpler and ***constant*** names
  - Example: `s.runes(1)` or `s.icon.gold`.
