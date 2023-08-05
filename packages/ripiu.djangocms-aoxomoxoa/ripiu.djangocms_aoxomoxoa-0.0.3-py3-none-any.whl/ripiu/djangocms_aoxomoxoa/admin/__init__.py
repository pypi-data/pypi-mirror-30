import operator
from functools import reduce

from ripiu.djangocms_aoxomoxoa.models.options import (
    SliderSavedUniteOptions, CarouselSavedUniteOptions,
    GridThemeSavedUniteOptions, TilesGridSavedUniteOptions,
    TilesNestedSavedUniteOptions, CompactThemeSavedUniteOptions,
    DefaultThemeSavedUniteOptions, TilesColumnsSavedUniteOptions,
    TilesJustifiedSavedUniteOptions,
)

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .options import (
    main, theme, tiles, slider, gallery, carousel, lightbox, thumbnail,
    grid_panel, navigation, strip_panel, tile_design, tile_text_panel,
    lightbox_text_panel,
)


class SavedUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = (
        (_(''), {
            'fields': (
                'name',
            ),
        }),
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        if hasattr(super(), 'fieldsets') and super().fieldsets:
            self.fieldsets = self.fieldsets + super().fieldsets


class CarouselUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.CarouselUniteOptionsAdmin.fieldsets,
        main.CarouselMainUniteOptionsAdmin.fieldsets,
        gallery.CarouselGalleryUniteOptionsAdmin.fieldsets,
        carousel.CarouselUniteOptionsAdmin.fieldsets,
        navigation.CarouselNavigationUniteOptionsAdmin.fieldsets,
        tile_design.TileDesignUniteOptionsAdmin.fieldsets,
        tile_text_panel.TileTextPanelUniteOptionsAdmin.fieldsets,
        lightbox.LightboxUniteOptionsAdmin.fieldsets,
        lightbox_text_panel.LightboxTextPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(CarouselSavedUniteOptions)
class CarouselSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                     CarouselUniteOptionsAdmin):
    pass


class CompactThemeUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.MinimalThemeUniteOptionsAdmin.fieldsets,
        gallery.SliderGalleryUniteOptionsAdmin.fieldsets,
        slider.SliderUniteOptionsAdmin.fieldsets,
        thumbnail.ThumbnailUniteOptionsAdmin.fieldsets,
        strip_panel.StripPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(CompactThemeSavedUniteOptions)
class CompactThemeSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                         CompactThemeUniteOptionsAdmin):
    pass


class DefaultThemeUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.DefaultThemeUniteOptionsAdmin.fieldsets,
        gallery.SliderGalleryUniteOptionsAdmin.fieldsets,
        slider.SliderUniteOptionsAdmin.fieldsets,
        thumbnail.ThumbnailUniteOptionsAdmin.fieldsets,
        strip_panel.StripPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(DefaultThemeSavedUniteOptions)
class DefaultThemeSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                         DefaultThemeUniteOptionsAdmin):
    pass


class GridThemeUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.MinimalThemeUniteOptionsAdmin.fieldsets,
        gallery.SliderGalleryUniteOptionsAdmin.fieldsets,
        slider.SliderUniteOptionsAdmin.fieldsets,
        thumbnail.ThumbnailUniteOptionsAdmin.fieldsets,
        grid_panel.GridPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(GridThemeSavedUniteOptions)
class GridThemeSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                      GridThemeUniteOptionsAdmin):
    pass


class SliderUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        gallery.SliderGalleryUniteOptionsAdmin.fieldsets,
        slider.SliderUniteOptionsAdmin.fieldsets,
    ])


@admin.register(SliderSavedUniteOptions)
class SliderSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                   SliderUniteOptionsAdmin):
    pass


class TilesColumnsUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.TilesColumnsThemeUniteOptionsAdmin.fieldsets,
        gallery.CarouselGalleryUniteOptionsAdmin.fieldsets,
        tiles.ColumnsTilesUniteOptionsAdmin.fieldsets,
        tile_design.TileDesignUniteOptionsAdmin.fieldsets,
        tile_text_panel.TileTextPanelUniteOptionsAdmin.fieldsets,
        lightbox.LightboxUniteOptionsAdmin.fieldsets,
        lightbox_text_panel.LightboxTextPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(TilesColumnsSavedUniteOptions)
class TilesColumnsSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                         TilesColumnsUniteOptionsAdmin):
    pass


class TilesGridUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.TilesGridUniteOptionsAdmin.fieldsets,
        main.TilesGridMainUniteOptionsAdmin.fieldsets,
        gallery.CarouselGalleryUniteOptionsAdmin.fieldsets,
        navigation.TilesGridNavigationUniteOptionsAdmin.fieldsets,
        tile_design.TileDesignUniteOptionsAdmin.fieldsets,
        tile_text_panel.TileTextPanelUniteOptionsAdmin.fieldsets,
        lightbox.LightboxUniteOptionsAdmin.fieldsets,
        lightbox_text_panel.LightboxTextPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(TilesGridSavedUniteOptions)
class TilesGridSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                      TilesGridUniteOptionsAdmin):
    pass


class TilesJustifiedUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.TilesThemeUniteOptionsAdmin.fieldsets,
        gallery.CarouselGalleryUniteOptionsAdmin.fieldsets,
        tiles.JustifiedTilesUniteOptionsAdmin.fieldsets,
        tile_design.TileDesignUniteOptionsAdmin.fieldsets,
        tile_text_panel.TileTextPanelUniteOptionsAdmin.fieldsets,
        lightbox.LightboxUniteOptionsAdmin.fieldsets,
        lightbox_text_panel.LightboxTextPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(TilesJustifiedSavedUniteOptions)
class TilesJustifiedSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                           TilesJustifiedUniteOptionsAdmin):
    pass


class TilesNestedUniteOptionsAdmin(admin.ModelAdmin):
    fieldsets = reduce(operator.add, [
        theme.TilesThemeUniteOptionsAdmin.fieldsets,
        gallery.CarouselGalleryUniteOptionsAdmin.fieldsets,
        tiles.NestedTilesUniteOptionsAdmin.fieldsets,
        tile_design.TileDesignUniteOptionsAdmin.fieldsets,
        tile_text_panel.TileTextPanelUniteOptionsAdmin.fieldsets,
        lightbox.LightboxUniteOptionsAdmin.fieldsets,
        lightbox_text_panel.LightboxTextPanelUniteOptionsAdmin.fieldsets,
    ])


@admin.register(TilesNestedSavedUniteOptions)
class TilesNestedSavedUniteOptionsAdmin(SavedUniteOptionsAdmin,
                                        TilesNestedUniteOptionsAdmin):
    pass
