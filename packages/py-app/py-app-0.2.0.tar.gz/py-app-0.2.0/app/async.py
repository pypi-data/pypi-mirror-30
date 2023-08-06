#
# Copyright (c) 2018 Eric Faurot <eric@faurot.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
import asyncio
import signal

import app.log
import app.run

_running = None
def stop():
    _running.cancel()

def start(func):
    global _running
    assert _running is None

    app.log.debug("async: starting")

    def _signal(signame):
        def _():
            app.log.debug("async: got signal %s", signame)
            if _running:
                _running.cancel()
        return _

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, _signal('SIGINT'))
    loop.add_signal_handler(signal.SIGTERM, _signal('SIGTERM'))

    try:
        _running = asyncio.ensure_future(func())
        loop.run_until_complete(_running)
    except asyncio.CancelledError:
        app.log.debug("async: cancelled")
    else:
        app.log.debug("async: stopped normally")
    finally:
        app.log.debug("async: closing event loop")
        loop.close()

    app.log.debug("async: done")
