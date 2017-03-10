from django.db import models
from django import forms
from multiselectfield import MultiSelectField
from users.models import MyUser
import re


def path_builder(instance, filename):
    filename = re.sub('[^a-zA-Z0-9\-\.]', '_', filename)

    return 'files/dynamics/{}/{}/{}'.format(
        instance.dynamic.user.email,
        instance.dynamic.id,
        filename
    )


class Box(models.Model):

    # Box Information
    box_dimension_x = models.IntegerField(default=0)
    box_dimension_y = models.IntegerField(default=0)
    box_dimension_z = models.IntegerField(default=0)
    box_coordinate_x = models.IntegerField(default=0)
    box_coordinate_y = models.IntegerField(default=0)
    box_coordinate_z = models.IntegerField(default=0)
    step = models.FloatField(default=1.0)

    # Probe
    CHOICES = (('COO-', 'COO-'),
               ('NH3+', 'NH3+'),
               ('CH3-', 'CH3-'),
               ('Ar(C-H)', 'Ar(C-H)'),
               ('O-H', 'O-H'),
               ('NH2', 'NH2'),
               ('Ar(N-H)', 'Ar(N-H)'),
               ('C=O', 'C=O'),
               ('NH2(ARG)', 'NH2(ARG)'),
               ('(H2O)HO', '(H2O)HO'),
               ('Zn2+', 'Zn2+'),
               ('Cl-', 'Cl-'),
               ('Na+', 'Na+'),)
    #probe = MultiSelectField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
    probe = MultiSelectField(choices=CHOICES)


class Dynamic(models.Model):
    # name = models.CharField(max_length=50)
    # email = models.EmailField()
    user = models.ForeignKey(MyUser)
    lqtagrid_box = models.ForeignKey(Box, default=None, null=True, blank=True)

    # Dynamic params
    box_size = models.IntegerField(default=10)
    number_of_molecules = models.IntegerField()
    number_of_atoms_for_alignment = models.IntegerField()

    # Flags
    configured = models.BooleanField(default=False)
    process_finished = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    run_dynamics = models.BooleanField(default=True)
    run_alignment = models.BooleanField(default=False)
    run_lqtagrid = models.BooleanField(default=False)

    started = models.DateField(auto_now_add=True)


class Molecule(models.Model):
    dynamic = models.ForeignKey(Dynamic)
    file = models.FileField(upload_to=path_builder)
    atoms = models.CharField(max_length=100)

    # Flag
    reference = models.BooleanField(default=False)
    # Flag
    dynamic_executed = models.BooleanField(default=False)
    alignment_executed = models.BooleanField(default=False)
    lqtagrid_executed = models.BooleanField(default=False)
