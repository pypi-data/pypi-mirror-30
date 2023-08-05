from django.db import models
from django.utils.translation import ugettext_lazy as _

from .constants import ALIGN_CENTER, ALIGN_CHOICES


class NavigationOptions(models.Model):
    '''
    Navigation options.
    Valid for:
      * Carousel
      * Tiles - Grid
    '''

    theme_navigation_align = models.CharField(
        _('navigation align'), max_length=6,
        default=ALIGN_CENTER, blank=False, choices=ALIGN_CHOICES,
        help_text=_('The align of the navigation.')
    )

    theme_navigation_offset_hor = models.PositiveSmallIntegerField(
        _('horizontal offset'),
        default=0, blank=False,
        # help_text=_('Horizontal offset of the navigation.')
    )

    theme_space_between_arrows = models.PositiveSmallIntegerField(
        _('space between arrows'),
        default=5, blank=False,
        help_text=_('The space between arrows in the navigation.')
    )

    class Meta:
        abstract = True


class CarouselNavigationOptions(NavigationOptions):
    '''
    Navigation options for Carousel
    '''
    POSITION_TOP = 'top'
    POSITION_BOTTOM = 'bottom'
    POSITION_CHOICES = (
        (POSITION_TOP, _('Top')),
        (POSITION_BOTTOM, _('Bottom')),
    )

    theme_enable_navigation = models.BooleanField(
        _('enable navigation'), default=True,
    )

    theme_navigation_enable_play = models.BooleanField(
        _('enable play'), default=True,
        help_text=_('enable / disable the play button of the navigation.')
    )

    theme_navigation_margin = models.PositiveSmallIntegerField(
        _('margin'),
        default=20, blank=False,
        help_text=_('The space between the carousel and the navigation.')
    )

    theme_navigation_position = models.CharField(
        _('position'), max_length=6,
        default=POSITION_BOTTOM, blank=False, choices=POSITION_CHOICES,
        help_text=_('The vertical position of the navigation reative to the '
                    'carousel.')
    )

    class Meta:
        abstract = True


class TilesGridNavigationOptions(NavigationOptions):
    '''
    Navigation options for Tiles - Grid
    '''
    COLOR_GRAY = 'gray'
    COLOR_BLUE = 'blue'
    COLOR_BROWN = 'brown'
    COLOR_GREEN = 'green'
    COLOR_RED = 'red'
    COLOR_CHOICES = (
        (COLOR_GRAY, _('Gray')),
        (COLOR_BLUE, _('Blue')),
        (COLOR_BROWN, _('Brown')),
        (COLOR_GREEN, _('Green')),
        (COLOR_RED, _('Red')),
    )
    NAV_TYPE_BULLETS = 'bullets'
    NAV_TYPE_ARROWS = 'arrows'
    NAV_TYPE_CHOICES = (
        (NAV_TYPE_BULLETS, _('Bullets')),
        (NAV_TYPE_ARROWS, _('Arrows')),
    )

    bullets_space_between = models.PositiveSmallIntegerField(
        _('space between bullets'),
        default=12, blank=False,
        # help_text=_('Space between bullets.')
    )

    grid_num_rows = models.PositiveSmallIntegerField(
        _('number of rows'),
        default=3, blank=False,
        help_text=_('Maximum number of grid rows. If set to big value, the '
                    'navigation will not appear.')
    )

    theme_arrows_margin_top = models.PositiveSmallIntegerField(
        _('arrows top margin'),
        default=20, blank=False,
        help_text=_('The space between arrows and grid.')
    )

    theme_bullets_color = models.CharField(
        _('bullet color'), max_length=6,
        default=COLOR_GRAY, blank=False, choices=COLOR_CHOICES,
        # help_text=_('Color of the bullets.')
    )

    theme_bullets_margin_top = models.PositiveSmallIntegerField(
        _('bullets top margin'),
        default=40, blank=False,
        help_text=_('The space between bullets and grid.')
    )

    theme_navigation_type = models.CharField(
        _('navigation type'), max_length=7,
        default=NAV_TYPE_BULLETS, blank=False, choices=NAV_TYPE_CHOICES,
        help_text=_('The vertical position of the navigation reative to the '
                    'carousel.')
    )

    class Meta:
        abstract = True
