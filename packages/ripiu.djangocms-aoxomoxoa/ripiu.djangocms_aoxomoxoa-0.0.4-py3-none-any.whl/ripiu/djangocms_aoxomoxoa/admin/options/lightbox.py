from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class LightboxUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    Tiles - Columns
    Tiles - Grid
    Tiles - Justified
    Tiles - Nested
    '''
    fieldsets = (
        (_('Lightbox options'), {
            'classes': ('collapse',),
            'fields': (
                'lightbox_type',

                'lightbox_hide_arrows_onvideoplay',
                'lightbox_arrows_position',
                ('lightbox_arrows_offset', 'lightbox_arrows_inside_offset',),
                'lightbox_arrows_inside_alwayson',

                'lightbox_overlay_color',
                ('lightbox_overlay_opacity', 'lightbox_top_panel_opacity',),

                'lightbox_close_on_emptyspace',

                'lightbox_show_numbers',
                ('lightbox_numbers_size', 'lightbox_numbers_color',),
                (
                    'lightbox_numbers_padding_top',
                    'lightbox_numbers_padding_right',
                ),

                'lightbox_slider_image_border',
                (
                    'lightbox_slider_image_border_width',
                    'lightbox_slider_image_border_radius',
                ),
                'lightbox_slider_image_border_color',

                'lightbox_slider_image_shadow',

                (
                    'lightbox_slider_control_swipe',
                    'lightbox_slider_control_zoom'
                ),
            )
        }),
    )
