# Generated by Django 4.0.5 on 2022-06-16 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_orderedtest_report_alter_orderedtest_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedtest',
            name='report',
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.TextField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.order')),
            ],
        ),
    ]