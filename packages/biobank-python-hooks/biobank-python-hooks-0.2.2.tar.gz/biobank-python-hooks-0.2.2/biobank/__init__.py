import requests, json
from django.apps import AppConfig
from fieldsignals import pre_save_changed
from kpi.models import Asset
from django.contrib.auth.models import User
from biobank.conf import settings
from biobank.biobank_backend import BiobankBackend


class BiobankConfig(AppConfig):
    name = 'biobank'

    def ready(self):
        def update_poll_slug(sender, instance, **kwargs):
            print(instance.username)

        def sendRequestToAPI(sender, instance=Asset, **kwargs):
            token = BiobankBackend.get_token(instance.owner.email)
            if token:
                headers = {'Authorization': 'Bearer {}'.format(token)}
                print(json.dumps(instance.content))
                r = requests.post(settings.API_URL + '/services/import',
                                  data={'title': instance.name, 'payload': json.dumps(instance.content), 'type': instance.asset_type, 'id': instance.uid},
                                  headers=headers)
                if r.status_code == requests.codes.ok:
                    response = r.json()
                    print(response)
                print(r)

        pre_save_changed.connect(sendRequestToAPI, sender=Asset, fields=['name', 'content'])
        pre_save_changed.connect(update_poll_slug, sender=User, fields=['username'])
