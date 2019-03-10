# Generated by Django 2.1.5 on 2019-02-16 03:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0013_auto_20190210_0959'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('serial', models.CharField(help_text='The serial of the certificate.', max_length=64)),
                ('pem', models.TextField(help_text='The full certificate as PEM.')),
                ('valid_from', models.DateTimeField(help_text='When this certificate was issued.')),
                ('valid_until', models.DateTimeField(help_text='When this certificate expires.')),
                ('first_seen', models.DateTimeField(help_text='When we first saw this certificate')),
                ('last_seen', models.DateTimeField(help_text='When we last saw this certificate')),
                ('ca', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='certificates', to='server.CertificateAuthority')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='server.Server')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='server',
            name='cert',
            field=models.ForeignKey(help_text='The current certificate used by this server.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='server.Certificate', verbose_name='Current certificate'),
        ),
    ]
