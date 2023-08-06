"""Index page handler package."""
from tornado.escape import url_unescape

from .baseHandler import BaseHandler


class CrudHandler(BaseHandler):
    """Arduino page handler."""

    def get(self, slug=None, method=None):
        """Handle get request."""
        if slug is None:
            self.list()
            return

        slug = url_unescape(slug)
        if slug == 'create':
            self.create()
        else:
            if method is None:
                self.show(slug)
            elif method == 'edit':
                self.edit(slug)
            elif method == 'create':
                self.create(slug)
            else:
                self.render("404.html")

    def post(self, slug=None, method=None):
        """
        Handle get request.

        Broswers can't send put and delete request so we have to fake them.
        """
        try:
            _method = self.get_argument('_method')
        except Exception:
            _method = None
        if slug is None and _method is None:
            self.store()
        elif _method is None:
            self.store(slug)
        slug = url_unescape(slug)

        if _method == 'put':
            self.put(slug, method)
        elif _method == 'delete':
            self.delete(slug, method)
        else:
            self.render("404.html")

    def put(self, slug, method=None):
        """Handle put request."""
        self.update(slug)

    def delete(self, slug, method=None):
        """Handle delete request."""
        self.destroy(slug)

    def list(self):
        """Show device."""
        pass

    def show(self, slug):
        """Show device."""
        pass

    def create(self, slug=None):
        """Show configuration form for device."""
        pass

    def edit(self, slug):
        """Show configuration form for device."""
        pass

    def store(self, slug):
        """Store configuration."""
        pass

    def update(self, slug):
        """Update configuration."""
        pass

    def destroy(self, slug):
        """Destroy configuration."""
        pass
