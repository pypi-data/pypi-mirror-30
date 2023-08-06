from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class TilesGridNavigationUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Grid
    '''
    fieldsets = (
        (_('Navigation options'), {
            'classes': ('collapse',),
            'fields': (
                'grid_num_rows',

                'theme_navigation_type',

                'theme_bullets_margin_top',
                'theme_bullets_color',
                'bullets_space_between',

                'theme_arrows_margin_top',
                'theme_space_between_arrows',

                'theme_navigation_align',
                'theme_navigation_offset_hor',
            )
        }),
    )


class CarouselNavigationUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    '''
    fieldsets = (
        (_('Navigation options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_enable_navigation',
                'theme_navigation_position',
                'theme_navigation_enable_play',
                'theme_navigation_align',
                'theme_navigation_offset_hor',
                'theme_navigation_margin',
                'theme_space_between_arrows',
            )
        }),
    )
