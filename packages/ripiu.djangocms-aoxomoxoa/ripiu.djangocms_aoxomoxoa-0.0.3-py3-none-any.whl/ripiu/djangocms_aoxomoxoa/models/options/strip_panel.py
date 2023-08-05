from colorfield.fields import ColorField

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from .constants import (
    ALIGN_LEFT, VALIGN_TOP, ALIGN_CHOICES, EASE_OUT_CUBIC, EASING_CHOICES,
    VALIGN_CHOICES,
)


class StripPanelOptions(models.Model):
    '''
    Strip panel options.
    Valid for:
      * Compact theme
      * Default theme
    '''
    ROLE_SCROLL_STRIP = 'scroll_strip'
    ROLE_ADVANCE_ITEM = 'advance_item'
    ROLE_CHOICES = (
        (ROLE_SCROLL_STRIP, _('Scroll strip')),
        (ROLE_ADVANCE_ITEM, _('Advance item')),
    )

    strippanel_background_color = ColorField(
        _('background color'),
        blank=True, default='',
        help_text=_('background color of the strip wrapper, if not set, it '
                    'will be taken from the CSS.')
    )

    strippanel_buttons_role = models.CharField(
        _('buttons role'), max_length=12,
        default=ROLE_SCROLL_STRIP, blank=False, choices=ROLE_CHOICES,
        help_text=_('Role of the side buttons.')
    )

    strippanel_buttons_skin = models.CharField(
        _('buttons skin'), max_length=255,
        blank=True, default='', choices=settings.RIPIU_AOXOMOXOA_UNITE_SKINS,
        help_text=_('Skin of the buttons, if empty inherit from gallery skin.')
    )

    strippanel_enable_buttons = models.BooleanField(
        _('enable buttons'), default=False,
        help_text=_('Enable buttons from the sides of the panel.')
    )

    strippanel_enable_handle = models.BooleanField(
        _('enable handle'), default=True,
    )

    strippanel_handle_align = models.CharField(
        _('handle alignment'), max_length=6,
        default=VALIGN_TOP, blank=False,
        choices=VALIGN_CHOICES + ALIGN_CHOICES,
        help_text=_('Close handle tip alignment on the handle bar according '
                    'panel orientation.')
    )

    strippanel_handle_offset = models.PositiveSmallIntegerField(
        _('handle offset'),
        default=0, blank=False,
        help_text=_('Offset of handle bar according the valign.')
    )

    strippanel_handle_skin = models.CharField(
        _('handle skin'), max_length=255,
        blank=True, default='', choices=settings.RIPIU_AOXOMOXOA_UNITE_SKINS,
        help_text=_('Skin of the handle, if empty inherit from gallery skin.')
    )

    strippanel_padding_bottom = models.PositiveSmallIntegerField(
        _('bottom padding'),
        default=8, blank=False,
        help_text=_('Space from bottom of the panel.')
    )

    strippanel_padding_buttons = models.PositiveSmallIntegerField(
        _('buttons padding'),
        default=2, blank=False,
        help_text=_('Padding between the buttons and the panel.')
    )

    strippanel_padding_left = models.PositiveSmallIntegerField(
        _('left padding'),
        default=0, blank=False,
        help_text=_('Space from left of the panel.')
    )

    strippanel_padding_right = models.PositiveSmallIntegerField(
        _('right padding'),
        default=0, blank=False,
        help_text=_('Space from right of the panel.')
    )

    strippanel_padding_top = models.PositiveSmallIntegerField(
        _('top padding'),
        default=8, blank=False,
        help_text=_('Space from top of the panel.')
    )

    strip_control_avia = models.BooleanField(
        _('avia control'), default=False,
        help_text=_('Move the strip according strip moseover position.')
    )

    strip_control_touch = models.BooleanField(
        _('touch control'), default=True,
        help_text=_('Move the strip by dragging it.')
    )

    strip_scroll_to_thumb_duration = models.PositiveSmallIntegerField(
        _('scroll animation duration'),
        default=500, blank=False,
        help_text=_('Duration of scrolling to thumb.')
    )

    strip_scroll_to_thumb_easing = models.CharField(
        _('scroll animation'), max_length=17,
        default=EASE_OUT_CUBIC, blank=False, choices=EASING_CHOICES,
        help_text=_('Easing of scrolling to thumb animation.')
    )

    strip_space_between_thumbs = models.PositiveSmallIntegerField(
        _('space between thumbnails'),
        default=6, blank=False,
    )

    strip_thumbs_align = models.CharField(
        _('thumbnail alignment'), max_length=6,
        default=ALIGN_LEFT, blank=False,
        choices=VALIGN_CHOICES + ALIGN_CHOICES,
        help_text=_('Alignment of the thumbnails when smaller than the strip '
                    'size.')
    )

    strip_thumb_touch_sensetivity = models.PositiveSmallIntegerField(
        _('touch sensitivity'),
        default=2, blank=False,
        validators=[MaxValueValidator(100)],
        help_text=_('1: most sensetive; 100: least sensetive.')
    )

    class Meta:
        abstract = True
