# Generated by Django 3.2 on 2025-05-04 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creators', '0001_initial'),
        ('accounts', '0005_user_last_uploaded_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='completed_surveys',
            field=models.ManyToManyField(blank=True, related_name='completed_by_users', to='creators.Survey'),
        ),
    ]
