from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]
    operations = [
        migrations.CreateModel(
            name='BusinessCustomerOrganisationGrafana',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organisation_id', models.IntegerField(default=0)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='organisation_grafana_business_customer', to='business.Business')),
            ]
        )
    ]