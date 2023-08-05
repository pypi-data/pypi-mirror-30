from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class CarouselUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    '''
    fieldsets = (
        (_('Carousel'), {
            'classes': ('collapse',),
            'fields': (
                'carousel_padding',
                'carousel_space_between_tiles',
                'carousel_navigation_numtiles',
                'carousel_scroll_duration',
                'carousel_scroll_easing',

                'carousel_autoplay',
                'carousel_autoplay_timeout',
                'carousel_autoplay_direction',
                'carousel_autoplay_pause_onhover',
            )
        }),
    )
