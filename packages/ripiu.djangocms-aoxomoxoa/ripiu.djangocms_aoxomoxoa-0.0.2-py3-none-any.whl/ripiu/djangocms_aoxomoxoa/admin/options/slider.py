from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class SliderUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Compact theme
    Default theme
    Grid theme
    Slider
    '''
    fieldsets = (
        (_('Navigation options'), {
            'classes': ('collapse',),
            'fields': (
                'slider_scale_mode',
                'slider_scale_mode_media',
                'slider_scale_mode_fullscreen',
                ('slider_item_padding_top', 'slider_item_padding_bottom',),
                ('slider_item_padding_left', 'slider_item_padding_right',),

                'slider_transition',
                ('slider_transition_speed', 'slider_transition_easing',),

                'slider_control_swipe',
                ('slider_control_zoom', 'slider_zoom_max_ratio',),
                ('slider_loader_type', 'slider_loader_color',),

                'slider_enable_bullets',
                'slider_bullets_skin',
                'slider_bullets_space_between',
                ('slider_bullets_align_hor', 'slider_bullets_align_vert',),
                ('slider_bullets_offset_hor', 'slider_bullets_offset_vert',),

                'slider_enable_arrows',
                'slider_arrows_skin',

                'slider_arrow_left_align_hor',
                'slider_arrow_left_align_vert',
                'slider_arrow_left_offset_hor',
                'slider_arrow_left_offset_vert',

                'slider_arrow_right_align_hor',
                'slider_arrow_right_align_vert',
                'slider_arrow_right_offset_hor',
                'slider_arrow_right_offset_vert',

                'slider_enable_progress_indicator',
                'slider_progress_indicator_type',
                'slider_progress_indicator_align_hor',
                'slider_progress_indicator_align_vert',
                'slider_progress_indicator_offset_hor',
                'slider_progress_indicator_offset_vert',

                'slider_progressbar_color',
                'slider_progressbar_opacity',
                'slider_progressbar_line_width',

                'slider_progresspie_type_fill',
                'slider_progresspie_color1',
                'slider_progresspie_color2',
                'slider_progresspie_stroke_width',
                'slider_progresspie_width',
                'slider_progresspie_height',

                'slider_enable_play_button',
                'slider_play_button_skin',
                'slider_play_button_align_hor',
                'slider_play_button_align_vert',
                'slider_play_button_offset_hor',
                'slider_play_button_offset_vert',

                'slider_enable_fullscreen_button',
                'slider_fullscreen_button_skin',
                'slider_fullscreen_button_align_hor',
                'slider_fullscreen_button_align_vert',
                'slider_fullscreen_button_offset_hor',
                'slider_fullscreen_button_offset_vert',

                'slider_enable_zoom_panel',
                'slider_zoompanel_skin',
                'slider_zoompanel_align_hor',
                'slider_zoompanel_align_vert',
                'slider_zoompanel_offset_hor',
                'slider_zoompanel_offset_vert',

                'slider_controls_always_on',
                'slider_controls_appear_ontap',
                'slider_controls_appear_duration',
                'slider_videoplay_button_type',

                'slider_enable_text_panel',
                'slider_textpanel_always_on',

                'slider_textpanel_text_valign',
                'slider_textpanel_padding_top',
                'slider_textpanel_padding_bottom',
                'slider_textpanel_height',
                'slider_textpanel_padding_title_description',
                'slider_textpanel_padding_right',
                'slider_textpanel_padding_left',
                'slider_textpanel_fade_duration',
                'slider_textpanel_enable_title',
                'slider_textpanel_enable_description',
                'slider_textpanel_enable_bg',
                'slider_textpanel_bg_color',
                'slider_textpanel_bg_opacity',

                'slider_textpanel_title_color',
                'slider_textpanel_title_font_family',
                'slider_textpanel_title_text_align',
                'slider_textpanel_title_font_size',
                'slider_textpanel_title_bold',
                'slider_textpanel_css_title',

                'slider_textpanel_desc_color',
                'slider_textpanel_desc_font_family',
                'slider_textpanel_desc_text_align',
                'slider_textpanel_desc_font_size',
                'slider_textpanel_desc_bold',
                'slider_textpanel_css_description',

                'slider_textpanel_bg_css',
            )
        }),
    )
