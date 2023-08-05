# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    # dependencies = [
    #     ('oauth_tokens.migrations', '0001_initial')
    # ]
    operations = [
        migrations.RunSQL(
            [
                "ALTER TABLE oauth_tokens_accesstoken ALTER COLUMN access_token TYPE varchar(2000);",
                "ALTER TABLE oauth_tokens_accesstoken ALTER COLUMN refresh_token TYPE varchar(1000);"
             ]
        ),
    ]
