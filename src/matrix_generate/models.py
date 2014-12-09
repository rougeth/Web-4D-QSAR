from django.db import models


def path_builder(instance, filename):
    filename = filename.replace(' ', '_')

    return 'files/matrix-dynamics/{}/{}/{}'.format(
        instance.matrix_generate.email,
        instance.matrix_generate.id,
        filename
    )


class MatrixGenerate(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()

    # Matrix Generate params
    number_of_molecules = models.IntegerField(default=1)

    # Flags
    configured = models.BooleanField(default=False)
    process_finished = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    started = models.DateField(auto_now_add=True)

class Molecule(models.Model):
    matrix_generate = models.ForeignKey(MatrixGenerate)
    file = models.FileField(upload_to=path_builder)

class Box(models.Model):
    matrix_generate = models.ForeignKey(MatrixGenerate)

    # Box Information
    box_dimension_x = models.IntegerField(default=3)
    box_dimension_y = models.IntegerField(default=3)
    box_dimension_z = models.IntegerField(default=3)
    box_coordinate_x = models.IntegerField(default=0)
    box_coordinate_y = models.IntegerField(default=0)
    box_coordinate_z = models.IntegerField(default=0)

    # Atoms Probe
    coo = models.BooleanField("COO-", default=False)
    nh3 = models.BooleanField("NH3+", default=False)
    ch3 = models.BooleanField("CH3-", default=False)
    arc = models.BooleanField("Ar(C-H, default=False)", default=False)
    oh = models.BooleanField("O-H", default=False)
    nh2 = models.BooleanField("NH2", default=False)
    arn = models.BooleanField("Ar(N-H, default=False)", default=False)
    c_o = models.BooleanField("C=O", default=False)
    sh = models.BooleanField("SH", default=False)
    nh2_arg = models.BooleanField("NH2(ARG, default=False)", default=False)
    h2o = models.BooleanField("(H2O, default=False)HO", default=False)
    zn2 = models.BooleanField("Zn2+", default=False)
    cl = models.BooleanField("Cl-", default=False)
    na = models.BooleanField("Na+", default=False)
