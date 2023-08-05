from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class TilesGridMainUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Tiles - Grid
    '''
    fieldsets = (
        (_('Main options'), {
            'classes': ('collapse',),
            'fields': (
                ('tile_width', 'tile_height',),

                'grid_padding',
                'grid_space_between_cols',
                'grid_space_between_rows',
            )
        }),
    )


class CarouselMainUniteOptionsAdmin(admin.ModelAdmin):
    '''
    Carousel
    '''
    fieldsets = (
        (_('Main options'), {
            'classes': ('collapse',),
            'fields': (
                ('tile_width', 'tile_height',),
            )
        }),
    )
