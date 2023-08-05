"""
SoakuBot Python, bot library for Overmobile's forums.
Made by Soaku aka RedClover from http://mrush.pl
"""

# Requests are required to connect to the Internet
# Colorama is used to add colors to the log
# Datetime is used to show timestamp in log
# Re is used to process regexes
# Inspect is required to show account data in log (ex. @http://mrush.pl:Nick)
# HTML is used to extract text from messages properly
import requests, colorama, datetime, re, inspect, html
# PyQuery is required to access HTML elements easily (i.e. read data from page)
from pyquery import PyQuery as pq
# urllib.parse is required to get details from URL, like thread page or thread id
import urllib.parse as urlparse
# To help fight with "too fast" dialog
import time
# To make life easier...
import typing

# Vars
debug = True
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/64.0.3282.186 Safari/537.36"
}


# Special classes
class Unknown: pass


# Command line options
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

# Load Colorama
if debug:
    # PyCharm requires setting specific Colorama options to work, detect if it's PyCharm and set them
    # import os
    # if 'PYCHARM_HOSTED' in os.environ: colorama.init(convert=False, strip=False); print("PyCharm detected")
    # else:
    colorama.init()


# Function by @Medeiros from Stackoverflow.com
def get_text(s):
    tag = False
    quote = False
    out = ""

    for c in s:
        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif (c == '"' or c == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + c

    # html.unescape entites
    return html.unescape(html.unescape(out))


def log(*msg, **kwarg):
    """
    Print a colored msg to the stdout containing the date.
    DO NOT use outside of the SB class or without extending it!
    (You can use it inside sub-class)
    type:
        0: normal
        1: warning
        2: error
        3: success
    """
    msg = " ".join(msg)
    if debug:
        color = colorama.Fore.WHITE

        if "type" in kwarg:
            type = kwarg["type"]
        else:
            type = 0

        if type == 1:
            color = colorama.Fore.YELLOW
        elif type == 2:
            color = colorama.Fore.RED
        elif type == 3:
            color = colorama.Fore.GREEN

        stack = inspect.stack()
        obj = stack[1][0].f_locals["self"]

        print(("[" + str(datetime.datetime.now()) + "]"), (color + msg + colorama.Fore.WHITE).strip().ljust(65),
              ("@" + obj.site + ":" + obj.nick))
    return msg


class connect:
    """
    Connect to any mrush website. Use of multiple accounts is allowed, but you must use different object for each.
    This class might be compatible with other OM games too, but it wasn't tested for that.
    """

    nick = None
    site = "http://mrush.pl"
    session = None
    space = False
    thspace = False
    wait = 5

    def __init__(self, nick: str, password: str, site: str = "http://mrush.pl"):
        self.site = site
        self.session = requests.Session()
        self.nick = nick
        self.session.headers.update(headers)

        log("\u2190\u2192 Connecting to", site, "as", nick)

        # login
        r = self.fast(lambda: self.session.post(self.site + '/login', {"name": nick, "password": password}), False)
        if 'name="name"' in r.text:
            log("- Failed to login", type=2)
            raise RuntimeError("Failed to login as " + nick + " on " + site)
        else:
            log("   Login success!", type=3)
            log("\u2190  Getting bot ID...")
            r = self.session.get(self.site + "/settings")
            self.id = pq(r.text).find(".cntr.mb5:not(.lorange)").eq(0).text()
            self.id = re.sub(r"\D+", "", self.id)
            log("   Success! It is", str(self.id), type=3)

    def __str__(self):
        return colorama.Fore.WHITE + " \t @" + self.site + ":" + self.nick

    def fast(self, l: typing.Callable, ref: typing.Callable=True):

        r = l()

        while True:

            if "zbyt szybko" in r.text:
                print("clicking too fast", self.wait)
                time.sleep(self.wait)
                self.wait += 1

                if callable(ref):
                    # Execute the action
                    r = ref()
                if ref:
                    # Refresh page
                    r = self.session.get(r.url)
                else:
                    # Or, resend request
                    r = l()

            else:
                if self.wait >= 10: self.wait -= 5
                return r

    @staticmethod
    def urlvar(var: str, url: str):
        """
        Get QS variable from URL
        """
        parsed = urlparse.urlparse(url)
        arr = urlparse.parse_qs(parsed.query)
        if var in arr:
            return arr[var][0]
        else:
            return None

    def forum(parent, id=0):
        """
        Get forum object for an existing category on the forums
        """

        class forum:
            site = "http://mrush.pl"

            def __init__(self):
                self.id = id
                self.nick = parent.nick
                self.site = parent.site
                self.session = parent.session

            def thread(self, name, msg):
                log(" \u2192 Creating thread", name)
                parent.thspace = not parent.thspace
                r = self.session.post(self.site + "/create_thread", {
                    "forum_id": str(self.id),
                    "thread_name": ("" if parent.thspace else " ") + name,
                    "thread_text": msg
                })
                i = int(parent.urlvar("id", r.url))
                res = parent.thread(i)
                res.title = name
                res.bbc = msg
                res.msg = msg
                res.id = i
                return res

            def scan(self, page=1):
                """ Full forum scan """

                log("\u2190  Scanning category", str(self.id))

                ret = []

                while True:
                    # print(CURSOR_UP_ONE + ERASE_LINE, end="")
                    log("\u2190  Scanning category", str(self.id), "page " + str(page))

                    r = parent.fast(
                        lambda: self.session.get(self.site + "/threads?id=" + str(self.id) + "&page=" + str(page))
                    )
                    p = pq(r.text)
                    q = p.find(".thread a")

                    for this in q.items():
                        t = parent.thread(parent.urlvar("id", this.attr("href")))
                        # if "." in this.text(): print(". in", this.text(), this.parent().html())
                        print(this.text())
                        t.title = this.text().strip()

                        # , t.title)

                        # TODO: Get status (new, pinned, closed)
                        # t.pinned = q.find("img")
                        ret.append(t)

                    if not p.find('img[src="http://144.76.127.94/view/image/art/ico-arr_right.png"]').length: return ret

                    page += 1

        return forum()

    def thread(parent, id=0):
        """
        Get thread object for an existing thread (by id), by ID or create new one (by title, msg).
        """

        class thread:
            id = 0
            msg = ""
            bbc = ""
            site = "http://mrush.pl"

            def __init__(self):
                self.id = id
                self.nick = parent.nick
                self.site = parent.site
                self.session = parent.session
                self._title = ""
                self.pinned = Unknown()
                self.closed = Unknown()
                self.new = Unknown()
                self.last_page = 0

            def __bool__(self):
                return bool(id)

            def list(self, f):
                """
                Parse HTML and read all posts
                """
                posts = []

                tag = f("[id^=msg]")

                def each(i, this):
                    creation = f(this).next()
                    msg = creation.next().find(".lblue")
                    author = parent.urlvar("player_id", creation.find("a").eq(0).attr("href"))
                    nick = creation.find("a.tdn.lwhite").text()

                    obj = parent.post(int(re.sub(r"\D", "", f(this).attr("id"))))
                    obj.html = str(msg.html())
                    obj.text = get_text(str(obj.html))
                    obj.author = {
                        "id": author,
                        "nick": nick
                    }
                    posts.append(obj)

                tag.each(each)

                return posts

            def read(self):
                """
                Read posts from last 2 pages of the thread.
                """

                log("\u2190  Reading posts from thread", str(id))

                # get thread url
                url = self.site + "/thread?id=" + str(self.id)
                r = parent.fast(lambda: parent.session.get(url))

                f = pq(r.text)
                temp = f('[alt="»"]').parents("a").attr("href")
                now = f("span.pag").eq(0).text()
                now = now if now else 1
                last = parent.urlvar("page", temp if temp else url)
                last = int(last if last else now)
                blast = str(max(last - 1, 1))
                last = str(last)

                posts = []
                self.last_page = int(last)

                r = self.session.get(url + "&page=" + blast)
                posts += self.list(pq(r.text))
                if (last != blast):
                    r = self.session.get(url + "&page=" + last)
                    posts += self.list(pq(r.text))
                return posts

            def reply(self, msg, to=0):
                """
                Post to the thread.
                :param msg: Message of the post
                :param to: ID of user this message will be sent to. 0 by default.
                :return: List of every post on the last page just after sending the message
                """

                log(" \u2192 Sending message to thread", str(self.id), "to player " + str(to) if to else "")
                sp = " " if parent.space else ""
                parent.space = not parent.space
                r = parent.fast(
                    lambda: parent.session.post(parent.site + "/thread_message", data={
                        "message_text": sp + msg.strip(),
                        "answer_id": to,
                        "thread_id": self.id,
                    })
                )
                return self.list(pq(r.text))

            def open(self):
                """
                Open the thread if closed.
                :return: self
                """

                log(" \u2192 Opening thread", str(self.id))
                self.session.get(self.site + "/open_thread?id=" + str(self.id))
                return self

            def close(self):
                """
                Close the thread if open
                :return: self
                """

                log(" \u2192 Closing thread", str(self.id))
                self.session.get(self.site + "/close_thread?id=" + str(self.id))
                return self

            def pin(self):
                """
                Pin the thread if not pinned
                :return: self
                """

                log(" \u2192 Pinning thread", str(self.id))
                self.session.get(self.site + "/attach_thread?id=" + str(self.id))
                return self

            def unpin(self):
                """
                Unpin the thread if pinned
                :return:
                """
                log(" \u2192 Unpinning thread", str(self.id))
                self.session.get(self.site + "/detach_thread?id=" + str(self.id))
                return self

            def edit(self, name, msg=Unknown(), insert=None):
                """ Edit thread title, optionally message. You can pass the third argument to insert the message
                to the current one at specific position. Use 0 to prepend, -1 to append.

                :param name: New name of the thread
                :param msg: New message, defaults to unchanged
                :param insert: Where to insert the new message; replace by default, set to int to append (-1),
                    prepend (0) or place somewhere else
                """

                r = parent.fast(lambda: self.session.get(self.site + "/edit_thread?id=" + str(self.id)))

                data = pq(r.text)
                log(" \u2192 Editing thread ", str(self.id), name)

                prev = html.unescape(data.find('[name=thread_text]').html() or "")
                # print(prev)

                if isinstance(msg, Unknown):
                    msg = prev
                elif isinstance(insert, int):

                    if insert < 0:
                        insert = len(prev) - insert
                    msg = prev[:insert] + msg + prev[insert:]

                fid = data.find("[name=first_message_id]").val()

                # print(msg)
                r = parent.fast(
                    lambda: self.session.post(self.site + "/update_thread", {
                        "thread_name": name,
                        "thread_text": msg,
                        "thread_id": str(self.id),
                        "first_message_id": fid,
                    })
                )
                return self

            def get_bbcode(self):
                """
                Get thread bbcode
                :return: self
                """
                log("\u2190  Getting BBCode of", str(self.id))
                r = parent.fast(lambda: self.session.get(self.site + "/edit_thread?id="+str(self.id)))
                self.bbc = pq(r.text).find("[name=thread_text]").html()
                return self.bbc

            def exists(self):
                """
                Check if the thread exists
                :return: boolean
                """
                r = self.session.get(self.site + "/thread?id=" + str(self.id))
                return not pq(r.text).find(".lose").length

        return thread()

    def post(parent, id):

        class post:
            id = 0
            site = "http://mrush.pl"
            text = ""
            html = ""
            bbc = ""
            author = {
                "id": 0,
                "nick": "",
            }

            def __init__(self):
                self.id = id
                self.site = parent.site
                self.nick = parent.nick
                self.session = parent.session

            def edit(self, msg):
                r = self.session.post(self.site + "/update_thread", {
                    "message_text": msg,
                    "message_id": str(self.id),
                })
                return self

            def get_bbcode(self):
                r = self.session.get(self.site + "/message_edit")
                self.bbc = pq(r.text).find("[name=message_text]").val()
                return self.bbc

        return post()

    def private(parent):

        class private:

            def __init__(self):
                self.site = parent.site
                self.session = parent.session

        return private()
