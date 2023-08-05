from django.db import models
from django.utils.translation import ugettext_lazy as _


class MainOptions(models.Model):
    '''
    Main options.
    Valid for:
      * Carousel
      * Tiles - Grid
    '''

    tile_height = models.PositiveSmallIntegerField(
        _('tile height'),
        default=150, blank=False,
        # help_text=_('Tile height.')
    )

    tile_width = models.PositiveSmallIntegerField(
        _('tile height'),
        default=180, blank=False,
        # help_text=_('Tile width.')
    )

    class Meta:
        abstract = True


class TilesGridMainOptions(MainOptions):
    '''
    Main options for Tiles - Grid
    '''

    grid_padding = models.PositiveSmallIntegerField(
        _('tile height'),
        default=10, blank=False,
        # help_text=_('Set padding to the grid.')
    )

    grid_space_between_cols = models.PositiveSmallIntegerField(
        _('space between columns'),
        default=20, blank=False,
        # help_text=_('Space between columns.')
    )

    grid_space_between_rows = models.PositiveSmallIntegerField(
        _('space between rows'),
        default=20, blank=False,
        # help_text=_('Space between rows.')
    )

    class Meta:
        abstract = True
