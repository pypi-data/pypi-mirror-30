from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class ThumbnailUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Compact theme
    Default theme
    Grid theme
    '''
    fieldsets = (
        (_('Thumbnail options'), {
            'classes': ('collapse',),
            'fields': (
                ('thumb_width', 'thumb_height',),
                'thumb_fixed_size',

                'thumb_border_effect',
                ('thumb_border_width', 'thumb_border_color',),
                ('thumb_over_border_width', 'thumb_over_border_color',),
                (
                    'thumb_selected_border_width',
                    'thumb_selected_border_color',
                ),

                'thumb_round_corners_radius',

                'thumb_color_overlay_effect',
                'thumb_overlay_color',
                'thumb_overlay_opacity',
                'thumb_overlay_reverse',

                'thumb_image_overlay_effect',
                'thumb_image_overlay_type',

                'thumb_transition_duration',
                'thumb_transition_easing',

                'thumb_show_loader',
                'thumb_loader_type',
            )
        }),
    )
