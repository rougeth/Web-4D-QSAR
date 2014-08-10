from django.db import models


def path_builder(instance, filename):
    return 'files/dynamics/{}/{}/{}'.format(
        instance.dynamic.email,
        instance.dynamic.id,
        filename
    )


class Dynamic(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()

    # Dynamic params
    box_size = models.IntegerField(default=10)
    number_of_molecules = models.IntegerField()
    number_of_atoms_for_alignment = models.IntegerField()

    # Flags
    configured = models.BooleanField(default=False)
    process_finished = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    started = models.DateField(auto_now_add=True)


class Molecule(models.Model):
    dynamic = models.ForeignKey(Dynamic)
    file = models.FileField(upload_to=path_builder)
    atoms = models.CharField(max_length=100)

    # Flag
    reference = models.BooleanField(default=False)
