from colorfield.fields import ColorField

from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from .constants import IMAGE_EFFECT_BW, IMAGE_EFFECT_CHOICES


class TileDesignOptions(models.Model):
    '''
    Tile design options.
    Valid for:
      * Carousel
      * Tiles - Columns
      * Tiles - Grid
      * Tiles - Justified
      * Tiles - Nested
    '''

    tile_as_link = models.BooleanField(
        _('act as link'), default=False,
        help_text=_('Make the tile act the tile as a link, no lightbox will '
                    'appear.')
    )

    tile_border_color = ColorField(
        _('border color'),
        blank=False, default='#F0F0F0',
        # help_text=_('Tile border color.')
    )

    tile_border_radius = models.PositiveSmallIntegerField(
        _('border radius'),
        blank=False,
        help_text=_('Tile border radius (applied to border only, not to '
                    'outline).')
    )

    tile_border_width = models.PositiveSmallIntegerField(
        _('border width'),
        default=3, blank=False,
        help_text=_('Tile border width.')
    )

    tile_enable_action = models.BooleanField(
        _('enable action'), default=True,
        help_text=_('Enable tile action on click like lightbox.')
    )

    tile_enable_border = models.BooleanField(
        _('enable border'),
        help_text=_('Enable border of the tile.')
    )

    tile_enable_icons = models.BooleanField(
        _('enable icons'), default=True,
        help_text=_('Enable icons in mouseover mode.')
    )

    tile_enable_image_effect = models.BooleanField(
        _('enable image effect'), default=False,
        # help_text=_('Enable tile image effect.')
    )

    tile_enable_outline = models.BooleanField(
        _('enable outline'), default=True,
        help_text=_('Enable outline of the tile (works only together with the '
                    'border).')
    )

    tile_enable_overlay = models.BooleanField(
        _('enable overlay'), default=True,
        help_text=_('Enable tile color overlay (on mouseover).')
    )

    tile_enable_shadow = models.BooleanField(
        _('enable shadow'), default=True,
        help_text=_('Enable shadow of the tile.')
    )

    tile_image_effect_reverse = models.BooleanField(
        _('enable effect reverse'), default=False,
        help_text=_('Reverce the image, set only on mouseover state.')
    )

    tile_image_effect_type = models.CharField(
        _('image effect type'), max_length=16,
        default=IMAGE_EFFECT_BW, blank=False, choices=IMAGE_EFFECT_CHOICES,
        # help_text=_('Tile effect type.')
    )

    tile_link_newpage = models.BooleanField(
        _('link newpage'), default=True,
        help_text=_('Open the tile link in new page.')
    )

    tile_outline_color = ColorField(
        _('outline color'),
        blank=False, default='#8B8B8B',
        # help_text=_('Tile outline color.')
    )

    tile_overlay_color = ColorField(
        _('overlay color'),
        blank=False, default='#000000',
        help_text=_('Tile overlay color.')
    )

    tile_overlay_opacity = models.PositiveSmallIntegerField(
        _('overlay opacity (%)'),
        blank=False, default=40,
        validators=[MaxValueValidator(100)],
        # help_text=_('Tile overlay opacity.')
    )

    tile_shadow_blur = models.PositiveSmallIntegerField(
        _('shadow blur'),
        default=3, blank=False,
        help_text=_('Shadow blur.')
    )

    tile_shadow_color = ColorField(
        _('shadow color'),
        blank=False, default='#8B8B8B',
        # help_text=_('Tile shadow color.')
    )

    tile_shadow_h = models.PositiveSmallIntegerField(
        _('shadow horizontal offset'),
        default=1, blank=False,
        help_text=_('Position of horizontal shadow.')
    )

    tile_shadow_spread = models.PositiveSmallIntegerField(
        _('shadow spread'),
        default=2, blank=False,
        # help_text=_('Shadow spread.')
    )

    tile_shadow_v = models.PositiveSmallIntegerField(
        _('shadow vertical offset'),
        default=1, blank=False,
        help_text=_('Position of vertical shadow.')
    )

    tile_show_link_icon = models.BooleanField(
        _('show link icon'), default=False,
        help_text=_('show link icon (if the tile has a link). In case of '
                    'tile_as_link this option not enabled.')
    )

    tile_space_between_icons = models.PositiveSmallIntegerField(
        _('space between icons'),
        default=26, blank=False,
        help_text=_('Initial space between icons, (on small tiles it may '
                    'change).')
    )

    class Meta:
        abstract = True


class TilesColumnsTileDesignOptions(TileDesignOptions):
    '''
    Tiles design options for Tiles - Columns
    '''

    class Meta:
        abstract = True


TilesColumnsTileDesignOptions._meta.get_field('tile_border_radius')\
    .default = 0
TilesColumnsTileDesignOptions._meta.get_field('tile_enable_border')\
    .default = False
TilesColumnsTileDesignOptions._meta.get_field('tile_enable_outline')\
    .default = False


class TilesJustifiedTileDesignOptions(TileDesignOptions):
    '''
    Tiles design options.
    Valid for:
      * Tiles - Justified
      * Tiles - Nested
    '''

    class Meta:
        abstract = True


TilesJustifiedTileDesignOptions._meta.get_field('tile_border_radius')\
    .default = 0
TilesJustifiedTileDesignOptions._meta.get_field('tile_enable_border')\
    .default = False
TilesJustifiedTileDesignOptions._meta.get_field('tile_enable_outline')\
    .default = False


class CarouselTileDesignOptions(TileDesignOptions):
    '''
    Tiles design options for Carousel
    '''

    class Meta:
        abstract = True


CarouselTileDesignOptions._meta.get_field('tile_border_radius')\
    .default = 0
CarouselTileDesignOptions._meta.get_field('tile_enable_border')\
    .default = True
CarouselTileDesignOptions._meta.get_field('tile_enable_outline')\
    .default = True


class TilesGridTileDesignOptions(TileDesignOptions):
    '''
    Tiles design options for Tiles - Grid
    '''

    class Meta:
        abstract = True


TilesGridTileDesignOptions._meta.get_field('tile_border_radius')\
    .default = 2
TilesGridTileDesignOptions._meta.get_field('tile_enable_border')\
    .default = True
TilesGridTileDesignOptions._meta.get_field('tile_enable_outline')\
    .default = False
