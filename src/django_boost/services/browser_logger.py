"""
Browser logger — JavaScript snippet for capturing browser console logs.

Equivalent to Laravel Boost's BrowserLogger.
"""


class BrowserLogger:
    """Manages the browser-side JavaScript logging snippet.

    The script captures console.log/warn/error, window errors,
    and unhandled rejections, sending them to /_boost/browser-logs.
    """

    @staticmethod
    def get_script() -> str:
        """Return the JS snippet as a string (for use in templates/middleware)."""
        return BOOST_JS_SOURCE

    @staticmethod
    def get_script_tag() -> str:
        """Return the script wrapped in <script> tags."""
        return f"<script>\n{BOOST_JS_SOURCE}\n</script>"


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
