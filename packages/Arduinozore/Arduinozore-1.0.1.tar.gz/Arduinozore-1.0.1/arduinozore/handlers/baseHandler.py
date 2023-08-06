"""Index page handler package."""
from settings import TEMPLATE_FOLDER
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    """Device page handler."""

    def get_template_path(self):
        """Get template path in order to find template files."""
        return TEMPLATE_FOLDER

    def prepare(self):
        """Prepare requests."""
        self.redirect_url = 'https://' + self.request.host
        self.redirect_url += self.request.uri.rstrip("/")

        if self.request.protocol == 'http':
            self.redirect(self.redirect_url, permanent=False)

    def set_default_headers(self, *args, **kwargs):
        """Set default headers."""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.set_header("Strict-Transport-Security",
                        "max-age=500; includeSubDomains; preload")
