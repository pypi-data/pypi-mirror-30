from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class TileTextPanelUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    Tiles - Columns
    Tiles - Grid
    Tiles - Justified
    Tiles - Nested
    '''
    fieldsets = (
        (_('Tile text panel options'), {
            'classes': ('collapse',),
            'fields': (
                ('tile_enable_textpanel', 'tile_textpanel_always_on',),
                'tile_textpanel_source',
                'tile_textpanel_appear_type',
                'tile_textpanel_position',
                'tile_textpanel_offset',

                (
                    'tile_textpanel_padding_top',
                    'tile_textpanel_padding_bottom',
                ),
                (
                    'tile_textpanel_padding_right',
                    'tile_textpanel_padding_left',
                ),
                ('tile_textpanel_bg_opacity', 'tile_textpanel_bg_color',),
                'tile_textpanel_bg_css',

                'tile_textpanel_title_color',
                'tile_textpanel_title_font_family',
                'tile_textpanel_title_text_align',
                'tile_textpanel_title_font_size',
                'tile_textpanel_title_bold',
                'tile_textpanel_css_title',

                'tile_textpanel_desc_color',
                'tile_textpanel_desc_font_family',
                'tile_textpanel_desc_text_align',
                'tile_textpanel_desc_font_size',
                'tile_textpanel_desc_bold',
                'tile_textpanel_css_description',
            )
        }),
    )
