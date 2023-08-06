from colorfield.fields import ColorField

from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from .constants import (
    EASE_OUT_QUAD, EASING_CHOICES, IMAGE_EFFECT_BW, IMAGE_EFFECT_CHOICES,
)


class ThumbnailOptions(models.Model):
    '''
    Thumbnail options
    Valid for:
      * Compact theme
      * Default theme
      * Grid theme
    '''
    LOADER_TYPE_DARK = 'dark'
    LOADER_TYPE_LIGHT = 'light'
    LOADER_TYPE_CHOICES = (
        (LOADER_TYPE_DARK, _('Dark')),
        (LOADER_TYPE_LIGHT, _('Light')),
    )

    WIDTH_FIXED = True
    WIDTH_DYNAMIC = False
    WIDTH_CHOICES = (
        (WIDTH_FIXED, _('Fixed')),
        (WIDTH_DYNAMIC, _('Dynamic')),
    )

    thumb_border_color = ColorField(
        _('border color'),
        blank=False, default='#000000',
    )

    thumb_border_effect = models.BooleanField(
        _('border effect'), default=True,
        help_text=_('Specify if the thumb has border.')
    )

    thumb_border_width = models.PositiveSmallIntegerField(
        _('border width'),
        default=0, blank=False,
    )

    thumb_color_overlay_effect = models.BooleanField(
        _('color overlay effect'), default=True,
        help_text=_('Thumbnail color overlay effect, release the overlay on '
                    'mouseover and selected states.')
    )

    thumb_fixed_size = models.BooleanField(
        _('sizing method'), default=WIDTH_FIXED, choices=WIDTH_CHOICES,
        help_text=_('Fixed/dynamic thumbnail width.')
    )

    thumb_height = models.PositiveSmallIntegerField(
        _('height'),
        default=50, blank=False,
    )

    thumb_image_overlay_effect = models.BooleanField(
        _('image overlay effect'), default=False,
        help_text=_('Images overlay effect on normal state only.')
    )

    thumb_image_overlay_type = models.CharField(
        _('image overlay type'), max_length=16,
        default=IMAGE_EFFECT_BW, blank=False, choices=IMAGE_EFFECT_CHOICES,
    )

    thumb_loader_type = models.CharField(
        _('loader type'), max_length=8,  blank=False,
        choices=LOADER_TYPE_CHOICES, default=LOADER_TYPE_DARK,
    )

    thumb_overlay_color = ColorField(
        _('overlay color'),
        blank=False, default='#000000',
    )

    thumb_overlay_opacity = models.PositiveSmallIntegerField(
        _('overlay opacity (%)'),
        blank=False, default=40,
        validators=[MaxValueValidator(100)],
        help_text=_('Thumbnail overlay color opacity.')
    )

    thumb_overlay_reverse = models.BooleanField(
        _('overlay reverse'), default=False,
        help_text=_('Reverse the overlay, will be shown on selected state '
                    'only.')
    )

    thumb_over_border_color = ColorField(
        _('mouseover border color'),
        blank=False, default='#D9D9D9',
        help_text=_('Thumbnail border color in mouseover state.')
    )

    thumb_over_border_width = models.PositiveSmallIntegerField(
        _('mouseover border width'),
        default=0, blank=False,
        help_text=_('Thumbnail border width in mouseover state.')
    )

    thumb_round_corners_radius = models.PositiveSmallIntegerField(
        _('border radius'),
        default=0, blank=False,
    )

    thumb_selected_border_color = ColorField(
        _('selected border color'),
        blank=False, default='#D9D9D9',
        help_text=_('Thumbnail border color in selected state.')
    )

    thumb_selected_border_width = models.PositiveSmallIntegerField(
        _('selected border width'),
        default=1, blank=False,
        help_text=_('Thumbnail border width in selected state.')
    )

    thumb_show_loader = models.BooleanField(
        _('show loader'), default=True,
        help_text=_('Show thumb loader while loading the thumb.')
    )

    thumb_transition_duration = models.PositiveSmallIntegerField(
        _('transition duration'),
        default=200, blank=False,
        help_text=_('Thumbnail effect transition duration.')
    )

    thumb_transition_easing = models.CharField(
        _('transition easing'), max_length=17,
        default=EASE_OUT_QUAD, blank=False, choices=EASING_CHOICES,
        help_text=_('Thumb effect transition easing.')
    )

    thumb_width = models.PositiveSmallIntegerField(
        _('width'),
        default=88, blank=False,
    )

    class Meta:
        abstract = True
