"""404 error handling package."""

from .baseHandler import BaseHandler


class My404Handler(BaseHandler):
    """404 error handler."""

    def prepare(self):
        """Override prepare to cover all possible HTTP methods."""
        if self.request.protocol == 'http':
            self.redirect('https://' + self.request.host +
                          self.request.uri, permanent=False)
        self.set_status(404)
        self.render("404.html")
