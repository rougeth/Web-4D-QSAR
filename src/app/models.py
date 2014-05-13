from time import strftime

from django.db import models


def path_builder(instance, filename):
    return 'files/dynamics/{}/{}/{}'.format(
        instance.dynamic.email,
        instance.dynamic.id,
        filename
    )

class Dynamic(models.Model):
    email = models.EmailField()
    # Gromacs params
    box_size_x = models.IntegerField(default=10)
    box_size_y = models.IntegerField(default=10)
    box_size_z = models.IntegerField(default=10)
    # Flags
    process_finished = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

class DynamicFile(models.Model):
    dynamic = models.ForeignKey(Dynamic)
    file = models.FileField(upload_to=path_builder)
