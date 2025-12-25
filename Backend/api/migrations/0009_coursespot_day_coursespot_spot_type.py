# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_travelspot_options_alter_review_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursespot',
            name='day',
            field=models.IntegerField(default=1, verbose_name='일차'),
        ),
        migrations.AddField(
            model_name='coursespot',
            name='spot_type',
            field=models.CharField(
                choices=[('travel', '여행지'), ('restaurant', '음식점'), ('accommodation', '숙박')],
                default='travel',
                max_length=20,
                verbose_name='장소 타입'
            ),
        ),
    ]
