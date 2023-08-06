from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class TileDesignUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    Tiles - Columns
    Tiles - Grid
    Tiles - Justified
    Tiles - Nested
    '''
    fieldsets = (
        (_('Tile design options'), {
            'classes': ('collapse',),
            'fields': (
                'tile_enable_border',
                'tile_border_width',
                ('tile_border_color', 'tile_border_radius',),

                'tile_enable_outline',
                'tile_outline_color',

                'tile_enable_shadow',
                ('tile_shadow_h', 'tile_shadow_v',),
                ('tile_shadow_blur', 'tile_shadow_spread',),
                'tile_shadow_color',

                'tile_enable_action',
                ('tile_as_link', 'tile_link_newpage',),

                'tile_enable_overlay',
                ('tile_overlay_opacity', 'tile_overlay_color'),

                ('tile_enable_icons', 'tile_show_link_icon',),
                'tile_space_between_icons',

                ('tile_enable_image_effect', 'tile_image_effect_reverse',),
                'tile_image_effect_type',
            )
        }),
    )
