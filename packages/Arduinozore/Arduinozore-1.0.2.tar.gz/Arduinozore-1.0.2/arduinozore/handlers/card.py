"""Index page handler package."""

from models.card import Card
from tornado.escape import url_escape

from .crudHandler import CrudHandler


class CardHandler(CrudHandler):
    """Card handler."""

    def list(self):
        """List configurations."""
        self.cards = Card.get_all()
        self.render('card/list.html', cards=self.cards)

    def show(self, slug):
        """Show device."""
        card = Card.get(slug)
        if card is not None:
            self.render('card/show.html', card=card, slug=slug)
        else:
            self.redirect('/card', permanent=False)

    def create(self):
        """Show configuration form for device."""
        settings = dict()
        settings['card'] = None
        settings['method'] = 'post'
        self.render('card/config.html', **settings)

    def edit(self, slug):
        """Show configuration form for device."""
        card = Card.get(slug)
        settings = dict()
        settings['card'] = card
        settings['method'] = 'put'
        self.render('card/config.html', **settings)

    def store(self, slug=""):
        """Create configuration."""
        card_name = self.get_argument('name')
        self.save(card_name)

    def update(self, slug):
        """Update configuration."""
        self.save(slug)

    def save(self, slug):
        """Save configuration."""
        card_name = slug
        nb_input_pins = self.get_argument('nb_input_pins')
        nb_output_pins = self.get_argument('nb_output_pins')
        card = Card(card_name, nb_input_pins, nb_output_pins)
        card.save()
        slug = url_escape(slug)
        redirect_url = self.redirect_url
        if slug not in redirect_url:
            redirect_url += '/' + slug
        self.redirect(redirect_url, permanent=True)

    def destroy(self, slug):
        """Destroy configuration."""
        card = Card.get(slug)
        card.delete()
        self.redirect(self.redirect_url, permanent=False)
