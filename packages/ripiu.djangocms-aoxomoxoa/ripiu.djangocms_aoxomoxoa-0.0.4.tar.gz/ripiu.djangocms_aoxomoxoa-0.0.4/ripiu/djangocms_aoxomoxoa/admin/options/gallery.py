from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class CarouselGalleryUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    Tiles - Columns
    Tiles - Grid
    Tiles - Justified
    Tiles - Nested
    '''
    fieldsets = (
        (_('Gallery options'), {
            'classes': ('collapse',),
            'fields': (
                # 'gallery_theme',
                'gallery_width',
                'gallery_min_width',
                'gallery_background_color',
            )
        }),
    )


class SliderGalleryUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Compact theme
    Default theme
    Grid theme
    Slider
    '''
    fieldsets = (
        (_('Gallery options'), {
            'classes': ('collapse',),
            'fields': (
                # 'gallery_theme',
                'gallery_width',
                'gallery_height',

                'gallery_min_width',
                'gallery_min_height',

                'gallery_skin',

                'gallery_images_preload_type',

                'gallery_autoplay',
                'gallery_play_interval',
                'gallery_pause_on_mouseover',

                'gallery_control_thumbs_mousewheel',
                'gallery_control_keyboard',
                'gallery_carousel',

                'gallery_preserve_ratio',
                'gallery_debug_errors',
                'gallery_background_color',
            )
        }),
    )
