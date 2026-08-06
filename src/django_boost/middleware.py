"""
Middleware to inject the Boost browser logger script into HTML responses.

Equivalent to Laravel Boost's InjectBoost middleware and @boostJs directive.
"""

import re

from django.http import HttpRequest, HttpResponse


class InjectBoost:
    """Middleware that injects the Boost JS snippet into HTML responses.

    The snippet captures browser console logs and sends them to the
    /_boost/browser-logs endpoint for AI debugging context.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._script: str | None = None

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        return self._inject_script(request, response)

    def _inject_script(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        if not self._should_inject(request, response):
            return response

        script = self._get_script()
        content = response.content.decode(response.charset or "utf-8")
        injected = re.sub(
            r"(</head>)",
            f"{script}\\1",
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        response.content = injected.encode(response.charset or "utf-8")
        if "Content-Length" in response.headers:
            del response.headers["Content-Length"]
        return response

    def _should_inject(self, request: HttpRequest, response: HttpResponse) -> bool:
        from .config import get_config

        if not get_config("enabled", True):
            return False
        if not get_config("browser_logs_watcher", True):
            return False
        content_type = response.get("Content-Type", "")
        return "text/html" in content_type and "x-frame" not in content_type.lower()

    def _get_script(self) -> str:
        if self._script is None:
            self._script = (
                "<script>\n"
                + BOOST_JS_SOURCE
                + "\n</script>"
            )
        return self._script

    @staticmethod
    def get_script() -> str:
        """Return the Boost JS snippet for use in template tags."""
        return BOOST_JS_SOURCE


BOOST_JS_SOURCE = r"""
(function() {
    var logs = [];
    var maxLogs = 100;
    var endpoint = '/_boost/browser-logs';
    var levels = ['error','warn','info','log','table'];
    function pushLog(type, data) {
        logs.push({type: type, data: data, timestamp: new Date().toISOString(), url: location.href, userAgent: navigator.userAgent});
        if (logs.length > maxLogs) logs.shift();
    }
    levels.forEach(function(lvl) {
        var orig = console[lvl];
        console[lvl] = function() {
            var args = Array.prototype.slice.call(arguments);
            try { pushLog(lvl, args.map(function(a) {
                try { return typeof a === 'object' ? JSON.parse(JSON.stringify(a)) : a; }
                catch(e) { return String(a); }
            })); } catch(e) {}
            return orig.apply(console, args);
        };
    });
    window.addEventListener('error', function(e) {
        pushLog('window_error', [{message: e.message, filename: e.filename, lineno: e.lineno, colno: e.colno, stack: e.error ? e.error.stack : void 0}]);
    });
    window.addEventListener('unhandledrejection', function(e) {
        pushLog('unhandled_rejection', [{message: 'Unhandled Promise Rejection', reason: String(e.reason)}]);
    });
    window.addEventListener('beforeunload', function() {
        if (!logs.length) return;
        var payload = JSON.stringify({logs: logs});
        if (navigator.sendBeacon) { navigator.sendBeacon(endpoint, payload); }
        else { try { var x = new XMLHttpRequest(); x.open('POST', endpoint, false); x.setRequestHeader('Content-Type', 'application/json'); x.send(payload); } catch(e) {} }
    });
})();
""".strip()
