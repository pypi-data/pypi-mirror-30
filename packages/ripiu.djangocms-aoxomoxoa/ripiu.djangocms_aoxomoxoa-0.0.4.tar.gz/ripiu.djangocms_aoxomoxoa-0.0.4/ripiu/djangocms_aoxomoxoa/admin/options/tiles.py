from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class JustifiedTilesUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Justified
    '''
    fieldsets = (
        (_('Tiles options'), {
            'classes': ('collapse',),
            'fields': (
                'tiles_enable_transition',
                'tiles_set_initial_height',
                # 'tiles_type',
                'tiles_justified_row_height',
                'tiles_justified_space_between',
            )
        }),
    )


class NestedTilesUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Nested
    '''
    fieldsets = (
        (_('Tiles options'), {
            'classes': ('collapse',),
            'fields': (
                'tiles_enable_transition',

                (
                    'tiles_space_between_cols',
                    'tiles_space_between_cols_mobile',
                ),
                'tiles_min_columns',
                # 'tiles_type',
                'tiles_nested_optimal_tile_width',
            )
        }),
    )


class ColumnsTilesUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Columns
    '''
    fieldsets = (
        (_('Tiles options'), {
            'classes': ('collapse',),
            'fields': (
                'tiles_col_width',
                'tiles_exact_width',
                'tiles_align',
                (
                    'tiles_space_between_cols',
                    'tiles_space_between_cols_mobile',
                ),
                'tiles_include_padding',
                ('tiles_min_columns', 'tiles_max_columns',),

                ('tiles_set_initial_height', 'tiles_enable_transition',),
            )
        }),
    )
