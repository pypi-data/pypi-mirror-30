from colorfield.fields import ColorField

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .constants import (
    ALIGN_LEFT, VALIGN_TOP, ALIGN_CHOICES, VALIGN_BOTTOM, VALIGN_MIDDLE,
    EASING_CHOICES, VALIGN_CHOICES, EASE_INOUT_QUAD,
)


class GridPanelOptions(models.Model):
    '''
    Grid panel options for Grid theme
    '''
    ARROWS_ALIGN_BORDERS = 'borders'
    ARROWS_ALIGN_CENTER = 'center'
    ARROWS_ALIGN_GRID = 'grid'
    ARROWS_ALIGN_MIDDLE = 'middle'
    ARROWS_ALIGN_CHOICES_H = (
        (ARROWS_ALIGN_BORDERS, _('Borders')),
        (ARROWS_ALIGN_CENTER, _('Center')),
        (ARROWS_ALIGN_GRID, _('Grid')),
    )
    # FIXME(geobaldi): don't repeat 'Borders' and 'Grid'
    ARROWS_ALIGN_CHOICES_V = (
        (ARROWS_ALIGN_BORDERS, _('Borders')),
        (ARROWS_ALIGN_MIDDLE, _('Middle')),
        (ARROWS_ALIGN_GRID, _('Grid')),
    )

    SCROLL_VERTICAL = True
    SCROLL_HORIZONTAL = False
    SCROLL_CHOICES = (
        (SCROLL_VERTICAL, _('Vertical')),
        (SCROLL_HORIZONTAL, _('Horizontal')),
    )

    PANES_DIRECTION_CHOICES = (
        (ALIGN_LEFT, _('Left')),
        (VALIGN_BOTTOM, _('Bottom')),
    )

    gridpanel_arrows_align_hor = models.CharField(
        _('arrows horizontal alignment'), max_length=7,
        default=ARROWS_ALIGN_CENTER, blank=False,
        choices=ARROWS_ALIGN_CHOICES_H,
        help_text=_('Horizontal alignment of arrows, to the left and right '
                    'borders, to the grid, or in the center space.')
    )

    gridpanel_arrows_align_vert = models.CharField(
        _('arrows vertical alignment'), max_length=7,
        default=ARROWS_ALIGN_MIDDLE, blank=False,
        choices=ARROWS_ALIGN_CHOICES_V,
        help_text=_('Vertical alignment of arrows, to the left and right '
                    'borders, to the grid, or in the center space.')
    )

    gridpanel_arrows_always_on = models.BooleanField(
        _('arrows always on'), default=False,
        help_text=_('Always show arrows even if the grid is one pane only.')
    )

    gridpanel_arrows_padding_hor = models.PositiveSmallIntegerField(
        _('horizontal arrows padding'),
        default=10, blank=False,
        help_text=_('In case of horizontal type only, minimal size from the '
                    'grid in case of "borders" and size from the grid in case '
                    'of "grid".')
    )

    gridpanel_arrows_padding_vert = models.PositiveSmallIntegerField(
        _('vertical arrows padding'),
        default=4, blank=False,
        help_text=_('Padding between the arrows and the grid, in case of '
                    '"middle" align, there will be minimal padding.')
    )

    gridpanel_arrows_skin = models.CharField(
        _('arrows skin'), max_length=255,
        blank=True, default='', choices=settings.RIPIU_AOXOMOXOA_UNITE_SKINS,
        help_text=_('Skin of the arrows, if blank inherit from gallery skin.')
    )

    gridpanel_background_color = ColorField(
        _('background color'),
        blank=True, default='',
        help_text=_('Background color of the grid wrapper, if not set, it '
                    'will be taken from the CSS.')
    )

    gridpanel_enable_handle = models.BooleanField(
        _('enable handle'), default=True,
    )

    gridpanel_grid_align = models.CharField(
        _('grid panel alignment'), max_length=6,
        default=VALIGN_MIDDLE, blank=False,
        choices=VALIGN_CHOICES + ALIGN_CHOICES,
    )

    gridpanel_handle_align = models.CharField(
        _('handle alignment'), max_length=6,
        default=VALIGN_TOP, blank=False,
        choices=VALIGN_CHOICES + ALIGN_CHOICES,
        help_text=_('Close handle tip align on the handle bar according panel '
                    'orientation.')
    )

    gridpanel_handle_offset = models.PositiveSmallIntegerField(
        _('handle offset'),
        default=0, blank=False,
        help_text=_('Offset of handle bar according the vertical align.')
    )

    gridpanel_handle_skin = models.CharField(
        _('handle'), max_length=255,
        blank=True, default='', choices=settings.RIPIU_AOXOMOXOA_UNITE_SKINS,
        help_text=_('Skin of the handle, if blank inherit from gallery skin.')
    )

    gridpanel_padding_border_bottom = models.PositiveSmallIntegerField(
        _('bottom padding'),
        default=4, blank=False,
        help_text=_('Padding between the bottom border of the panel.')
    )

    gridpanel_padding_border_left = models.PositiveSmallIntegerField(
        _('left padding'),
        default=10, blank=False,
        help_text=_('Padding between the left border of the panel.')
    )

    gridpanel_padding_border_right = models.PositiveSmallIntegerField(
        _('right padding'),
        default=10, blank=False,
        help_text=_('Padding between the left border of the panel.')
    )

    gridpanel_padding_border_top = models.PositiveSmallIntegerField(
        _('top padding'),
        default=4, blank=False,
        help_text=_('Padding between the top border of the panel.')
    )

    gridpanel_space_between_arrows = models.PositiveSmallIntegerField(
        _('space between arrows'),
        default=20, blank=False,
        help_text=_('On horizontal grids only.')
    )

    gridpanel_vertical_scroll = models.BooleanField(
        _('scroll direction'), default=SCROLL_VERTICAL, choices=SCROLL_CHOICES,
        help_text=_('Vertical or horizontal grid scroll and arrows.')
    )

    grid_carousel = models.BooleanField(
        _('carousel'), default=False,
        help_text=_('Next pane goes to first when on last.')
    )

    grid_num_cols = models.PositiveSmallIntegerField(
        _('columns'),
        default=2, blank=False,
        help_text=_('Number of grid columns.')
    )

    grid_panes_direction = models.CharField(
        _('panes direction'), max_length=6,
        default=ALIGN_LEFT, blank=False,
        choices=PANES_DIRECTION_CHOICES,
        help_text=_('Where panes will move')
    )

    grid_space_between_cols = models.PositiveSmallIntegerField(
        _('space between columns'),
        default=10, blank=False,
    )

    grid_space_between_rows = models.PositiveSmallIntegerField(
        _('space between rows'),
        default=10, blank=False,
    )

    grid_transition_duration = models.PositiveSmallIntegerField(
        _('transition duration (ms)'),
        default=300, blank=False,
        help_text=_('Transition of the panes change duration.')
    )

    grid_transition_easing = models.CharField(
        _('transition easing'), max_length=17,
        default=EASE_INOUT_QUAD, blank=False, choices=EASING_CHOICES,
        help_text=_('Easing function for the pane change transition.')
    )

    class Meta:
        abstract = True
