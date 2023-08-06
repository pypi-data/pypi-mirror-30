from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class GridPanelUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Grid theme
    '''
    fieldsets = (
        (_('Strip panel options'), {
            'classes': ('collapse',),
            'fields': (
                'gridpanel_vertical_scroll',
                'gridpanel_grid_align',
                (
                    'gridpanel_padding_border_top',
                    'gridpanel_padding_border_bottom',
                ),
                (
                    'gridpanel_padding_border_left',
                    'gridpanel_padding_border_right',
                ),

                'gridpanel_arrows_skin',
                ('gridpanel_arrows_align_vert', 'gridpanel_arrows_align_hor',),
                (
                    'gridpanel_arrows_padding_vert',
                    'gridpanel_arrows_padding_hor',
                ),

                'gridpanel_space_between_arrows',
                'gridpanel_arrows_always_on',

                'gridpanel_enable_handle',
                'gridpanel_handle_align',
                'gridpanel_handle_offset',
                'gridpanel_handle_skin',

                'gridpanel_background_color',

                'grid_panes_direction',
                'grid_num_cols',
                'grid_space_between_cols',
                'grid_space_between_rows',
                'grid_transition_duration',
                'grid_transition_easing',
                'grid_carousel',
            )
        }),
    )
