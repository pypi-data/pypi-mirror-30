from django.db import models
from django.utils.translation import ugettext_lazy as _

from .main import MainOptions, TilesGridMainOptions
from .theme import (
    GridThemeOptions, TilesThemeOptions, CompactThemeOptions,
    DefaultThemeOptions, CarouselThemeOptions, TilesGridThemeOptions,
    TilesColumnsThemeOptions,
)
from .tiles import (
    NestedTilesOptions, ColumnsTilesOptions, JustifiedTilesOptions,
)
from .slider import SliderOptions
from .gallery import SliderGalleryOptions, TilesCarouselGalleryOptions
from .carousel import CarouselOptions
from .lightbox import LightboxOptions
from .thumbnail import ThumbnailOptions
from .grid_panel import GridPanelOptions
from .navigation import CarouselNavigationOptions, TilesGridNavigationOptions
from .strip_panel import StripPanelOptions
from .tile_design import (
    CarouselTileDesignOptions, TilesGridTileDesignOptions,
    TilesColumnsTileDesignOptions, TilesJustifiedTileDesignOptions,
)
from .tile_text_panel import TileTextPanelOptions
from .lightbox_text_panel import LightboxTextPanelOptions

__all__ = [
    'CarouselSavedUniteOptions',
    'CarouselUniteOptions',
    'CompactThemeSavedUniteOptions',
    'CompactThemeUniteOptions',
    'DefaultThemeSavedUniteOptions',
    'DefaultThemeUniteOptions',
    'GridThemeSavedUniteOptions',
    'GridThemeUniteOptions',
    'SavedUniteOptions',
    'SliderSavedUniteOptions',
    'SliderUniteOptions',
    'TilesColumnsSavedUniteOptions',
    'TilesColumnsUniteOptions',
    'TilesGridSavedUniteOptions',
    'TilesGridUniteOptions',
    'TilesJustifiedSavedUniteOptions',
    'TilesJustifiedUniteOptions',
    'TilesNestedSavedUniteOptions',
    'TilesNestedUniteOptions',
]


class SavedUniteOptions(models.Model):
    '''
    Saved unite options
    '''

    name = models.CharField(
        _('name'), max_length=255
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        abstract = True


class CarouselUniteOptions(CarouselThemeOptions,
                           MainOptions,
                           TilesCarouselGalleryOptions,
                           CarouselOptions,
                           CarouselNavigationOptions,
                           CarouselTileDesignOptions,
                           TileTextPanelOptions,
                           LightboxOptions,
                           LightboxTextPanelOptions):
    '''
    Carousel unite options
    '''

    class Meta:
        abstract = True


class CarouselSavedUniteOptions(SavedUniteOptions,
                                CarouselUniteOptions):
    '''
    Carousel saved unite options
    '''

    class Meta:
        verbose_name = _('Carousel unite options')
        verbose_name_plural = _('Carousel unite options')


class CompactThemeUniteOptions(CompactThemeOptions,
                               SliderGalleryOptions,
                               SliderOptions,
                               ThumbnailOptions,
                               StripPanelOptions):
    '''
    Compact theme unite options
    '''

    class Meta:
        abstract = True


class CompactThemeSavedUniteOptions(SavedUniteOptions,
                                    CompactThemeUniteOptions):
    '''
    Compact theme saved unite options
    '''

    class Meta:
        verbose_name = _('Compact theme unite options')
        verbose_name_plural = _('Compact theme unite options')


class DefaultThemeUniteOptions(DefaultThemeOptions,
                               SliderGalleryOptions,
                               SliderOptions,
                               ThumbnailOptions,
                               StripPanelOptions):
    '''
    Default theme unite options
    '''

    class Meta:
        abstract = True


class DefaultThemeSavedUniteOptions(SavedUniteOptions,
                                    DefaultThemeUniteOptions):
    '''
    Default theme saved unite options
    '''

    class Meta:
        verbose_name = _('Default theme unite options')
        verbose_name_plural = _('Default theme unite options')


class GridThemeUniteOptions(GridThemeOptions,
                            SliderGalleryOptions,
                            SliderOptions,
                            ThumbnailOptions,
                            GridPanelOptions):
    '''
    Grid theme unite options
    '''

    class Meta:
        abstract = True


class GridThemeSavedUniteOptions(SavedUniteOptions,
                                 GridThemeUniteOptions):
    '''
    Grid theme saved unite options
    '''

    class Meta:
        verbose_name = _('Grid theme unite options')
        verbose_name_plural = _('Grid theme unite options')


class SliderUniteOptions(SliderGalleryOptions,
                         SliderOptions):
    '''
    Slider unite options
    '''

    class Meta:
        abstract = True


class SliderSavedUniteOptions(SavedUniteOptions,
                              SliderUniteOptions):
    '''
    Slider saved unite options
    '''

    class Meta:
        verbose_name = _('Slider unite options')
        verbose_name_plural = _('Slider unite options')


class TilesColumnsUniteOptions(TilesColumnsThemeOptions,
                               TilesCarouselGalleryOptions,
                               ColumnsTilesOptions,
                               TilesColumnsTileDesignOptions,
                               TileTextPanelOptions,
                               LightboxOptions,
                               LightboxTextPanelOptions):
    '''
    Tiles - Columns unite options
    '''

    class Meta:
        abstract = True


class TilesColumnsSavedUniteOptions(SavedUniteOptions,
                                    TilesColumnsUniteOptions):
    '''
    Tiles - Columns saved unite options
    '''

    class Meta:
        verbose_name = _('Tiles - Columns unite options')
        verbose_name_plural = _('Tiles - Columns unite options')


class TilesGridUniteOptions(TilesGridThemeOptions,
                            TilesGridMainOptions,
                            TilesCarouselGalleryOptions,
                            TilesGridNavigationOptions,
                            TilesGridTileDesignOptions,
                            TileTextPanelOptions,
                            LightboxOptions,
                            LightboxTextPanelOptions):
    '''
    Tiles - Grid unite options
    '''

    class Meta:
        abstract = True


class TilesGridSavedUniteOptions(SavedUniteOptions,
                                 TilesGridUniteOptions):
    '''
    Tiles - Grid saved unite options
    '''

    class Meta:
        verbose_name = _('Tiles - Grid unite options')
        verbose_name_plural = _('Tiles - Grid unite options')


class TilesJustifiedUniteOptions(TilesThemeOptions,
                                 TilesCarouselGalleryOptions,
                                 JustifiedTilesOptions,
                                 TilesJustifiedTileDesignOptions,
                                 TileTextPanelOptions,
                                 LightboxOptions,
                                 LightboxTextPanelOptions):
    '''
    Tiles - Justified unite options
    '''

    class Meta:
        abstract = True


class TilesJustifiedSavedUniteOptions(SavedUniteOptions,
                                      TilesJustifiedUniteOptions):
    '''
    Tiles - Justified savedunite options
    '''

    class Meta:
        verbose_name = _('Tiles - Justified unite options')
        verbose_name_plural = _('Tiles - Justified unite options')


class TilesNestedUniteOptions(TilesThemeOptions,
                              TilesCarouselGalleryOptions,
                              NestedTilesOptions,
                              TilesJustifiedTileDesignOptions,
                              TileTextPanelOptions,
                              LightboxOptions,
                              LightboxTextPanelOptions):
    '''
    Tiles - Nested unite options
    '''

    class Meta:
        abstract = True


class TilesNestedSavedUniteOptions(SavedUniteOptions,
                                   TilesNestedUniteOptions):
    '''
    Tiles - Nested saved unite options
    '''

    class Meta:
        verbose_name = _('Tiles - Nested unite options')
        verbose_name_plural = _('Tiles - Nested unite options')
