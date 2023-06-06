# Generated by Django 4.2 on 2023-04-24 23:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Webinar',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('title', models.CharField(max_length=300, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание вебинара')),
                ('content', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Медиа')),
                ('webinar_started_date', models.DateTimeField()),
                ('calendar_link', models.URLField(verbose_name='Ссылка на календарь')),
                ('webinar_link', models.URLField(verbose_name='Ссылка на вебинар')),
            ],
            options={
                'verbose_name': 'Вебинар',
                'verbose_name_plural': 'Вебинары',
            },
        ),
    ]
