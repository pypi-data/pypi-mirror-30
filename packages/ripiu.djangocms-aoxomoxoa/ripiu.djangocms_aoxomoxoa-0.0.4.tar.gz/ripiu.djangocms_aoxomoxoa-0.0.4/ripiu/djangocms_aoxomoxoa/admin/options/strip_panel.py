from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class StripPanelUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Compact theme
    Default theme
    '''
    fieldsets = (
        (_('Strip panel options'), {
            'classes': ('collapse',),
            'fields': (
                ('strippanel_padding_top', 'strippanel_padding_bottom',),

                ('strippanel_padding_left', 'strippanel_padding_right',),

                'strippanel_enable_buttons',
                'strippanel_buttons_skin',
                'strippanel_padding_buttons',

                'strippanel_buttons_role',

                'strippanel_enable_handle',
                'strippanel_handle_align',
                'strippanel_handle_offset',
                'strippanel_handle_skin',

                'strippanel_background_color',

                'strip_thumbs_align',
                'strip_space_between_thumbs',
                'strip_thumb_touch_sensetivity',
                'strip_scroll_to_thumb_duration',
                'strip_scroll_to_thumb_easing',
                'strip_control_avia',
                'strip_control_touch',
            )
        }),
    )
