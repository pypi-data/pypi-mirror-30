
# Generated by Django 1.10.6 on 2017-03-23 13:45


from django.db import migrations, models
import octo_drf.apps.base.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PDFTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=255, unique=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0448\u0430\u0431\u043b\u043e\u043d\u0430')),
                ('template', models.CharField(editable=False, help_text='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 HTML \u0448\u0430\u0431\u043b\u043e\u043d\u0430. \u0421\u043e\u0437\u0434\u0430\u0435\u0442\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438, \u043d\u0430 \u043e\u0441\u043d\u043e\u0432\u0435 \u0438\u043c\u0435\u043d\u0438\u0415\u0441\u043b\u0438 \u043e\u0434\u043d\u043e\u0438\u043c\u0435\u043d\u043d\u043e\u0433\u043e \u0448\u0430\u0431\u043b\u043e\u043d\u0430 \u043d\u0435\u0442\u0443 \u0432 \u043f\u0430\u043f\u043a\u0435, \u043e\u043d \u0431\u0443\u0434\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u043d \u0430\u0432\u0442\u043e\u043c\u0430\u0447\u0435\u0441\u043a\u0438', max_length=255, verbose_name='HTML \u0448\u0430\u0431\u043b\u043e\u043d')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('content', models.TextField(blank=True, verbose_name='\u041a\u043e\u043d\u0442\u0435\u043d\u0442')),
                ('footer', models.TextField(blank=True, verbose_name='\u0424\u0443\u0442\u0435\u0440')),
            ],
            options={
                'verbose_name': 'PDF \u0448\u0430\u0431\u043b\u043e\u043d',
                'verbose_name_plural': 'PDF \u0448\u0430\u0431\u043b\u043e\u043d\u044b',
            },
            bases=(octo_drf.apps.base.models.DynamicModelFieldsMixin, models.Model),
        ),
    ]
