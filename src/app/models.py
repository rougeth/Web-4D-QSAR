from time import strftime

from django.db import models


def path_builder(instance, filename):
    return 'files/dynamics/{}/{}/{}'.format(
        strftime('%Y/%m/%d'),
        instance.email,
        filename
    )

class Dynamic(models.Model):
    email = models.EmailField()
    zip_file = models.FileField(upload_to=path_builder)
    # Gromacs params
    box_size_x = models.IntegerField(default=10)
    box_size_y = models.IntegerField(default=10)
    box_size_z = models.IntegerField(default=10)
    # Flags
    process_finished = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
