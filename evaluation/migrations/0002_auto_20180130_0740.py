# Generated by Django 2.0.1 on 2018-01-30 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerdata',
            name='marks',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='answerdata',
            name='question',
            field=models.TextField(default=2),
            preserve_default=False,
        ),
    ]