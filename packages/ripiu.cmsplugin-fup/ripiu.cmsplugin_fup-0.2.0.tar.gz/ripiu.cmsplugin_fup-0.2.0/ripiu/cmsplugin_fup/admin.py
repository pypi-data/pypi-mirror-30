from django.contrib import admin

from .models import FUPItemPosition, FUPItemAnimation, FUPItemAnimationFrame


class FUPItemPositionInline(admin.TabularInline):
    model = FUPItemPosition
    extra = 0
    min_num = 2
    max_num = 2


class FUPItemAnimationFrameInline(admin.TabularInline):
    model = FUPItemAnimationFrame


@admin.register(FUPItemAnimation)
class FUPItamAnimationAdmin(admin.ModelAdmin):
    inlines = [FUPItemAnimationFrameInline]
    prepopulated_fields = {'slug': ('name',)}
