from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class LightboxTextPanelUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    Tiles - Columns
    Tiles - Grid
    Tiles - Justified
    Tiles - Nested
    '''
    fieldsets = (
        (_('Lightbox text panel'), {
            'classes': ('collapse',),
            'fields': (
                'lightbox_show_textpanel',
                'lightbox_textpanel_width',

                (
                    'lightbox_textpanel_enable_title',
                    'lightbox_textpanel_enable_description',
                ),

                (
                    'lightbox_textpanel_padding_top',
                    'lightbox_textpanel_padding_bottom',
                ),
                (
                    'lightbox_textpanel_padding_right',
                    'lightbox_textpanel_padding_left',
                ),

                'lightbox_textpanel_title_color',
                'lightbox_textpanel_title_font_family',
                'lightbox_textpanel_title_text_align',
                'lightbox_textpanel_title_font_size',
                'lightbox_textpanel_title_bold',
                'lightbox_textpanel_css_title',

                'lightbox_textpanel_desc_color',
                'lightbox_textpanel_desc_font_family',
                'lightbox_textpanel_desc_text_align',
                'lightbox_textpanel_desc_font_size',
                'lightbox_textpanel_desc_bold',
                'lightbox_textpanel_css_description',
            )
        }),
    )
