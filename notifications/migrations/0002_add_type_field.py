from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(
                choices=[
                    ('movement', 'Movimiento'),
                    ('stock_low', 'Stock bajo'),
                    ('order', 'Pedido'),
                    ('alert', 'Alerta'),
                    ('info', 'Información'),
                ],
                default='info',
                max_length=20
            ),
        ),
    ]