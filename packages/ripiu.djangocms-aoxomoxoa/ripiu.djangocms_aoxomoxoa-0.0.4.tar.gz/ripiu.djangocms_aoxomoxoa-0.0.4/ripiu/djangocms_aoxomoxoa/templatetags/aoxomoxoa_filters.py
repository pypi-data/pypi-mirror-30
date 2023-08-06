from django.template import Library

register = Library()


@register.filter(name='get_size')
def get_size(thumb_opt):
    return (thumb_opt.width, thumb_opt.height)


@register.filter(name='get_alt')
def get_alt(instance):
    if hasattr(instance, 'image'):
        # cmsplugin_filer_image
        return instance.alt_text or instance.image.default_alt_text
    if hasattr(instance, 'picture'):
        # djangocms_picture
        if 'alt' in instance.attributes and instance.attributes['alt']:
            return instance.attributes['alt']
        return instance.picture.default_alt_text
    return 'PUPPA!'


@register.filter(name='get_caption')
def get_caption(instance):
    if hasattr(instance, 'image'):
        # cmsplugin_filer_image
        return instance.caption_text or instance.image.default_caption
    if hasattr(instance, 'picture'):
        # djangocms_picture
        return instance.caption_text or instance.picture.default_caption
