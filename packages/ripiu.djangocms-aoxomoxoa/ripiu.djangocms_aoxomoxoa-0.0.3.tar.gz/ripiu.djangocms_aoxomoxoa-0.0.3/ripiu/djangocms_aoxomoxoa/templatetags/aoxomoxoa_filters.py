from django.template import Library

register = Library()


@register.filter(name='get_size')
def get_size(thumb_opt):
    return '%(w)dx%(h)d' % {
        'w': thumb_opt.width,
        'h': thumb_opt.height,
    }
