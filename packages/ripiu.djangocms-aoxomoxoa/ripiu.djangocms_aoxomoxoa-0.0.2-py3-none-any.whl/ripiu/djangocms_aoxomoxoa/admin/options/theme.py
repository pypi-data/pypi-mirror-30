from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class MinimalThemeUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Compact Theme
    Grid Theme
    '''
    fieldsets = (
        (_('Theme options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_hide_panel_under_width',
                'theme_panel_position',
            )
        }),
    )


class DefaultThemeUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Default Theme
    '''
    fieldsets = (
        (_('Theme options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_hide_panel_under_width',
                'theme_enable_fullscreen_button',
                'theme_enable_hidepanel_button',
                'theme_enable_play_button',
                'theme_enable_text_panel',
                'theme_text_align',
                'theme_text_padding_left',
                'theme_text_padding_right',
                'theme_text_type',
            )
        }),
    )


class CarouselUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    '''
    fieldsets = (
        (_('Theme options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_gallery_padding',
                'theme_carousel_align',
                'theme_carousel_offset',
            )
        }),
    )


class TilesGridUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Grid
    '''
    fieldsets = (
        (_('Theme options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_auto_open',
                'theme_gallery_padding',
            )
        }),
    )


class TilesThemeUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Justified
    Tiles - Nested
    '''
    fieldsets = (
        (_('Theme options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_gallery_padding',
                'theme_enable_preloader',
                'theme_preloading_height',
                'theme_preloader_vertpos',
                'theme_auto_open',
            )
        }),
    )


class TilesColumnsThemeUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Columns
    '''
    fieldsets = (
        (_('Theme options'), {
            'classes': ('collapse',),
            'fields': (
                'theme_gallery_padding',
                'theme_enable_preloader',
                'theme_preloading_height',
                'theme_preloader_vertpos',
                'theme_auto_open',
                'theme_appearance_order',
            )
        }),
    )
