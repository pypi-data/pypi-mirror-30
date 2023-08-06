from cms.models import CMSPlugin
from colorfield.fields import ColorField

from django.db import models
from django.utils.translation import ugettext_lazy as _

# from cms.models.fields import PageField
# from filer.fields.image import FilerImageField

PX = 'px'
REM = 'rem'
PERCENT = '%'
VW = 'vw'
VH = 'vh'

UNIT_CHOICES = (
    (PX, _('pixel')),
    (REM, _('root em')),
    (PERCENT, '%'),
    (VW, _('vw')),
    (VH, _('vh')),
)


class FUPItemAnimation(models.Model):
    """An animation is a collection of frames"""

    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=25, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Animation')
        verbose_name_plural = _('Animations')


class FUPItemPluginModel(CMSPlugin):
    """A FUP item is a unit inside a FUP container"""

    background_color = ColorField(
        _('background color'), null=True
    )

    width = models.DecimalField(
        _('width'),
        max_digits=5, decimal_places=2,
        blank=False
    )

    width_unit = models.CharField(
        _('unit'), max_length=5,
        choices=UNIT_CHOICES, default=PX
    )

    max_width = models.DecimalField(
        _('maximum width'),
        max_digits=5, decimal_places=2,
        null=True, blank=True
    )

    max_width_unit = models.CharField(
        _('unit'), max_length=5,
        choices=UNIT_CHOICES, default=PX
    )

    height = models.DecimalField(
        _('height'),
        max_digits=5, decimal_places=2,
        blank=False
    )

    height_unit = models.CharField(
        _('unit'), max_length=5,
        choices=UNIT_CHOICES, default=PX
    )

    max_height = models.DecimalField(
        _('maximum height'),
        max_digits=5, decimal_places=2,
        null=True, blank=True
    )

    max_height_unit = models.CharField(
        _('unit'), max_length=5,
        choices=UNIT_CHOICES, default=PX
    )

    animation = models.ForeignKey(
        FUPItemAnimation, blank=True, null=True,
        on_delete=models.SET_NULL
    )

    animation_duration = models.DecimalField(
        _('duration (s)'),
        default=0.7,
        max_digits=3, decimal_places=1, blank=False
    )

    def copy_relations(self, oldinstance):
        self.animation = oldinstance.animation
        self.fupitemposition_set.all().delete()
        for position in oldinstance.fupitemposition_set.all():
            position.pk = None
            position.fup_item = self
            position.save()

    def __str__(self):
        return ''

    class Meta:
        verbose_name = _('FUP item')
        verbose_name_plural = _('FUP items')


class FUPContainerPluginModel(CMSPlugin):
    """A FUP item container"""

    name = models.SlugField(_('name'), max_length=50, blank=False)

    def __str__(self):
        fup = self.fuppluginmodel_set.first()
        if fup:
            return '%s (%s)' % (self.name, fup.name)
        return self.name


class FUPPluginModel(CMSPlugin):
    """A FUP is a beautiful thing"""

    name = models.CharField(_('name'), max_length=255)
    # Can't be a OneToOneField: the published and the draft one have the same
    # value here
    fup_container = models.ForeignKey(
        FUPContainerPluginModel, blank=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Just return name"""
        return self.name

    class Meta:
        verbose_name = _('FUP')
        verbose_name_plural = _('FUPs')


class FUPItemPosition(models.Model):
    """A position of a FUP item"""

    x = models.DecimalField(
        'x',
        max_digits=7, decimal_places=3, blank=False
    )
    x_unit = models.CharField(
        _('unit'),
        max_length=5, choices=UNIT_CHOICES
    )
    y = models.DecimalField(
        'y',
        max_digits=7, decimal_places=3, blank=False
    )
    y_unit = models.CharField(
        _('unit'),
        max_length=5, choices=UNIT_CHOICES
    )
    fup_item = models.ForeignKey(
        FUPItemPluginModel, blank=False, null=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '(%f%s, %f%s)' % (self.x, self.x_unit, self.y, self.y_unit)

    class Meta:
        verbose_name = _('FUP item position')
        verbose_name_plural = _('FUP item positions')


class FUPItemAnimationFrame(models.Model):
    x = models.SmallIntegerField('x', blank=False)
    y = models.SmallIntegerField('y', blank=False)
    z = models.SmallIntegerField('z', blank=False)
    # frame_number = models.SmallIntegerField(_("frame"), blank=False)
    animation = models.ForeignKey(
        FUPItemAnimation,
        blank=False, null=False,
        on_delete=models.CASCADE,
        related_name='frames',
        related_query_name='frame'
    )

    def __str__(self):
        return '(%d, %d, %d)' % (self.x, self.y, self.z)

    class Meta:
        verbose_name = _('Animation frame')
        verbose_name_plural = _('Animation frames')
