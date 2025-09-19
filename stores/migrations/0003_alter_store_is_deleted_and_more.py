import django.db.models.deletion
from django.conf import settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_remove_store_address'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='storeitem',
            name='discount_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='storeitem',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.CreateModel(
            name='SellerRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pendign', 'Pending'), ('approved', 'Approved'), ('regected', 'Rejected')], default='pernding', max_length=10)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sellerrequest_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
