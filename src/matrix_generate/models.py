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
    coo = models.BooleanField("COO-")
    nh3 = models.BooleanField("NH3+")
    ch3 = models.BooleanField("CH3-")
    arc = models.BooleanField("Ar(C-H)")
    oh = models.BooleanField("O-H")
    nh2 = models.BooleanField("NH2")
    arn = models.BooleanField("Ar(N-H)")
    c_o = models.BooleanField("C=O")
    sh = models.BooleanField("SH")
    nh2_arg = models.BooleanField("NH2(ARG)")
    h2o = models.BooleanField("(H2O)HO")
    zn2 = models.BooleanField("Zn2+")
    cl = models.BooleanField("Cl-")
    na = models.BooleanField("Na+")
