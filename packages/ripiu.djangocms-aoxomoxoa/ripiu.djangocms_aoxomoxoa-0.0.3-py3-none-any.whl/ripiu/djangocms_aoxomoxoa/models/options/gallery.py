from colorfield.fields import ColorField

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class GalleryOptions(models.Model):
    '''
    Gallery options.
    Valid for:
      * Carousel
      * Compact theme
      * Default theme
      * Grid theme
      * Slider
      * Tiles - Columns
      * Tiles - Grid
      * Tiles - Justified
      * Tiles - Nested
    '''

    gallery_background_color = ColorField(
        _('background color'),
        blank=True, default='',
        help_text=_('set custom background color. If not set it will be '
                    'taken from css.')
    )

    gallery_min_width = models.PositiveSmallIntegerField(
        _('minimum width'),
        blank=False,
        help_text=_('Gallery minimum width when resizing.')
    )

    class Meta:
        abstract = True


class TilesCarouselGalleryOptions(GalleryOptions):
    '''
    Gallery options.
    Valid for:
      * Carousel
      * Tiles - Columns
      * Tiles - Justified
      * Tiles - Nested
    '''

    gallery_width = models.CharField(
        _('width'), max_length=8,
        default='100%', blank=False,
        help_text=_('Gallery width.')
    )

    class Meta:
        abstract = True


TilesCarouselGalleryOptions._meta.get_field('gallery_min_width').default = 150


class SliderGalleryOptions(GalleryOptions):
    '''
    Gallery options.
    Valid for:
      * Compact theme
      * Default theme
      * Grid theme
      * Slider
    '''
    PRELOAD_ALL = 'all'
    PRELOAD_MINIMAL = 'minimal'
    PRELOAD_VISIBLE = 'visible'
    PRELOAD_CHOICES = (
        (PRELOAD_ALL, _('load all the images first time')),
        (PRELOAD_MINIMAL, _('only image nabours will be loaded each time')),
        (PRELOAD_VISIBLE, _('visible thumbs images will be loaded each time')),
    )

    gallery_skin = models.CharField(
        _('gallery skin'), max_length=255,
        blank=False, choices=settings.RIPIU_AOXOMOXOA_UNITE_SKINS,
        # help_text=_('Gallery skin.')
    )

    gallery_width = models.PositiveSmallIntegerField(
        _('width'),
        default=900, blank=False,
        help_text=_('Gallery width.')
    )

    # gallery_min_width = models.PositiveSmallIntegerField(
    #     _('minimum width'),
    #     default=400, blank=False,
    #     help_text=_('Gallery minimum width when resizing.')
    # )

    gallery_autoplay = models.BooleanField(
        _('gallery autoplay'), default=False,
        help_text=_('Begin slideshow autoplay on start.')
    )

    gallery_carousel = models.BooleanField(
        _('carousel'), default=True,
        help_text=_('Next button on last image goes to first image.')
    )

    gallery_control_keyboard = models.BooleanField(
        _('keyboard'), default=True,
        help_text=_('Enable / disable keyboard controls.')
    )

    gallery_control_thumbs_mousewheel = models.BooleanField(
        _('mousewheel'), default=False,
        help_text=_('Enable / disable the mousewheel.')
    )

    gallery_debug_errors = models.BooleanField(
        _('debug errors'), default=True,
        help_text=_('show error message when there is some error on the '
                    'gallery area.')
    )

    gallery_height = models.PositiveSmallIntegerField(
        _('height'),
        default=500, blank=False,
        help_text=_('Gallery height.')
    )

    gallery_images_preload_type = models.CharField(
        _('preload type'), max_length=8,
        default=PRELOAD_MINIMAL, blank=False,
        choices=PRELOAD_CHOICES,
        help_text=_('Preload type of the images.')
    )

    gallery_min_height = models.PositiveSmallIntegerField(
        _('minimum height'),
        default=300, blank=False,
        help_text=_('Gallery minimal height when resizing.')
    )

    gallery_pause_on_mouseover = models.BooleanField(
        _('pause on mouseover'), default=False,
        help_text=_('Pause on mouseover when playing slideshow.')
    )

    gallery_play_interval = models.PositiveSmallIntegerField(
        _('play interval'),
        default=3000, blank=False,
        help_text=_('Play interval of the slideshow.')
    )

    gallery_preserve_ratio = models.BooleanField(
        _('carousel'), default=True,
        help_text=_('Preserve aspect ratio on window resize.')
    )

    class Meta:
        abstract = True


SliderGalleryOptions._meta.get_field('gallery_min_width').default = 400
