# Generated by Django 5.0.4 on 2024-04-20 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idr_colas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breakdownidrcolas',
            name='jde',
            field=models.CharField(blank=True, choices=[('Janvier', 'Janvier'), ('Fevrier', 'Février'), ('Mars', 'Mars'), ('Avril', 'Avril'), ('Mai', 'Mai'), ('Juin', 'Juin'), ('Juillet', 'Juillet'), ('Aout', 'Août'), ('Septembre', 'Septembre'), ('Octobre', 'October'), ('Novembre', 'Novembre'), ('Decembre', 'Décembre')], max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='breakdownidrcolas',
            name='month',
            field=models.CharField(blank=True, choices=[('Janvier', 'Janvier'), ('Fevrier', 'Février'), ('Mars', 'Mars'), ('Avril', 'Avril'), ('Mai', 'Mai'), ('Juin', 'Juin'), ('Juillet', 'Juillet'), ('Aout', 'Août'), ('Septembre', 'Septembre'), ('Octobre', 'October'), ('Novembre', 'Novembre'), ('Decembre', 'Décembre')], max_length=50, null=True),
        ),
    ]
