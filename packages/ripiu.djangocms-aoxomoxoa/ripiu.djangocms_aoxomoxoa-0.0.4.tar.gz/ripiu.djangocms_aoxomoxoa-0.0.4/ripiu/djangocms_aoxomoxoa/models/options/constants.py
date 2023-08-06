from django.db import models  # NOQA
from django.utils.translation import ugettext_lazy as _

ALIGN_LEFT = 'left'
ALIGN_CENTER = 'center'
ALIGN_RIGHT = 'right'
ALIGN_CHOICES = (
    (ALIGN_LEFT, _('Left')),
    (ALIGN_CENTER, _('Center')),
    (ALIGN_RIGHT, _('Right')),
)

VALIGN_TOP = 'top'
VALIGN_MIDDLE = 'middle'
VALIGN_BOTTOM = 'bottom'
VALIGN_CHOICES = (
    (VALIGN_TOP, _('Top')),
    (VALIGN_MIDDLE, _('Middle')),
    (VALIGN_BOTTOM, _('Bottom')),
)

POSITION_TOP = 'top'
POSITION_BOTTOM = 'bottom'
POSITION_LEFT = 'left'
POSITION_RIGHT = 'right'
POSITION_CHOICES = (
    (POSITION_TOP, _('Top')),
    (POSITION_BOTTOM, _('Bottom')),
    (POSITION_LEFT, _('Left')),
    (POSITION_RIGHT, _('Right')),
)

EASE_INOUT_BACK = 'easeInOutBack'
EASE_INOUT_BOUNCE = 'easeInOutBounce'
EASE_INOUT_CIRC = 'easeInOutCirc'
EASE_INOUT_CUBIC = 'easeInOutCubic'
EASE_INOUT_ELASTIC = 'easeInOutElastic'
EASE_INOUT_EXPO = 'easeInOutExpo'
EASE_INOUT_QUAD = 'easeInOutQuad'
EASE_INOUT_QUART = 'easeInOutQuart'
EASE_INOUT_QUINT = 'easeInOutQuint'
EASE_INOUT_SINE = 'easeInOutSine'
EASE_IN_BACK = 'easeInBack'
EASE_IN_BOUNCE = 'easeInBounce'
EASE_IN_CIRC = 'easeInCirc'
EASE_IN_CUBIC = 'easeInCubic'
EASE_IN_ELASTIC = 'easeInElastic'
EASE_IN_EXPO = 'easeInExpo'
EASE_IN_QUAD = 'easeInQuad'
EASE_IN_QUART = 'easeInQuart'
EASE_IN_QUINT = 'easeInQuint'
EASE_IN_SINE = 'easeInSine'
EASE_OUT_BACK = 'easeOutBack'
EASE_OUT_BOUNCE = 'easeOutBounce'
EASE_OUT_CIRC = 'easeOutCirc'
EASE_OUT_CUBIC = 'easeOutCubic'
EASE_OUT_ELASTIC = 'easeOutElastic'
EASE_OUT_EXPO = 'easeOutExpo'
EASE_OUT_QUAD = 'easeOutQuad'
EASE_OUT_QUART = 'easeOutQuart'
EASE_OUT_QUINT = 'easeOutQuint'
EASE_OUT_SINE = 'easeOutSine'
EASE_SWING = 'swing'
EASING_CHOICES = (
    (EASE_INOUT_BACK,  _('easeInOutBack')),
    (EASE_INOUT_BOUNCE,  _('easeInOutBounce')),
    (EASE_INOUT_CIRC,  _('easeInOutCirc')),
    (EASE_INOUT_CUBIC,  _('easeInOutCubic')),
    (EASE_INOUT_ELASTIC,  _('easeInOutElastic')),
    (EASE_INOUT_EXPO,  _('easeInOutExpo')),
    (EASE_INOUT_QUAD,  _('easeInOutQuad')),
    (EASE_INOUT_QUART,  _('easeInOutQuart')),
    (EASE_INOUT_QUINT,  _('easeInOutQuint')),
    (EASE_INOUT_SINE,  _('easeInOutSine')),
    (EASE_IN_BACK,  _('easeInBack')),
    (EASE_IN_BOUNCE,  _('easeInBounce')),
    (EASE_IN_CIRC,  _('easeInCirc')),
    (EASE_IN_CUBIC,  _('easeInCubic')),
    (EASE_IN_ELASTIC,  _('easeInElastic')),
    (EASE_IN_EXPO,  _('easeInExpo')),
    (EASE_IN_QUAD,  _('easeInQuad')),
    (EASE_IN_QUART,  _('easeInQuart')),
    (EASE_IN_QUINT,  _('easeInQuint')),
    (EASE_IN_SINE,  _('easeInSine')),
    (EASE_OUT_BACK,  _('easeOutBack')),
    (EASE_OUT_BOUNCE,  _('easeOutBounce')),
    (EASE_OUT_CIRC,  _('easeOutCirc')),
    (EASE_OUT_CUBIC,  _('easeOutCubic')),
    (EASE_OUT_ELASTIC,  _('easeOutElastic')),
    (EASE_OUT_EXPO,  _('easeOutExpo')),
    (EASE_OUT_QUAD,  _('easeOutQuad')),
    (EASE_OUT_QUART,  _('easeOutQuart')),
    (EASE_OUT_QUINT,  _('easeOutQuint')),
    (EASE_OUT_SINE,  _('easeOutSine')),
    (EASE_SWING,  _('swing')),
)

APPEAR_SLIDE = 'slide'
APPEAR_FADE = 'fade'
APPEAR_CHOICES = (
    (APPEAR_SLIDE, _('Slide')),
    (APPEAR_FADE, _('Fade')),
)

IMAGE_EFFECT_BW = 'bw'
IMAGE_EFFECT_BLUR = 'blur'
IMAGE_EFFECT_SEPIA = 'sepia'
IMAGE_EFFECT_CHOICES = (
    (IMAGE_EFFECT_BW, _('Black and white')),
    (IMAGE_EFFECT_BLUR, _('Blur')),
    (IMAGE_EFFECT_SEPIA, _('Sepia')),
)
