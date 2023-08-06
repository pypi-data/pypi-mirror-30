from collections import OrderedDict

from django.contrib import admin


class AomoxoaModelAdmin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        result = ()
        classes = list(OrderedDict.fromkeys(
            [c for c in self.__class__.mro() if hasattr(c, 'fieldsets')]
        ))
        for cls in classes:
            if cls.fieldsets:
                result += cls.fieldsets
        return result
