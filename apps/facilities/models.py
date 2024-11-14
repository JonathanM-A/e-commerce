from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Facility(models.Model):
    name = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=False)
    region = models.CharField(max_length=255, null=False)
    country = models.CharField(max_length=255, null=False)
    staff_number = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=300, unique=True, null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            combined_string = f"{self.name}-{self.city}"
            self.slug = slugify(combined_string)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "facility"
        verbose_name_plural = "facilities"

    def __str__(self):
        return f"{self.name}, {self.city.title()}"

@receiver(pre_save, sender=Facility)
def facility_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        base_slug = slugify(instance.name)
        slug = base_slug
        num = 1
        while Facility.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        instance.slug = slug





# Base Model
# Created at, Modified at/Updated at
# UUID, Slug