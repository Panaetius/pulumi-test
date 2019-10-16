from base64 import b64encode

import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Namespace, Service, Secret
from pulumi_kubernetes.extensions.v1beta1 import Ingress
#from pulumi_random.random_pet import RandomPet
from pulumi_random.random_password import RandomPassword

app_labels = { "app": "nginx" }

config = pulumi.Config()
k8s_config = pulumi.Config("kubernetes")

#release = config.get('release') or RandomPet("Release").id
password = config.get('password') or RandomPassword("password", length=32, special=True, number=True, upper=True)

secret = Secret(
    "credentials",
    data={
        "username": b64encode(b"admin").decode('ascii'),
        "password": password.result.apply(lambda p: b64encode(p.encode()).decode('ascii'))
    })

deployment = Deployment(
    "test-deployment",
    spec={
        "selector": { "match_labels": app_labels },
        "replicas": 2,
        "template": {
            "metadata": { "labels": app_labels },
            "spec": {
                "containers": [{
                     "name": "nginx",
                     "image": "nginx",
                     "volumeMounts":[{
                        "name": "secret-volume",
                        "mountPath": "/etc/secret-volume"
                        }]
                     }],
                "volumes":[{
                    "name": "secret-volume",
                    "secret":{
                        "secretName": secret.metadata['name']
                    }
                }]
            }
        }
    })

service = Service(
    "service",
    spec={
        "selector": app_labels,
        "ports":
        [{
            "port": 80,
        }]
    }
)

hostname = "{}.dev.renku.ch".format(k8s_config.require("namespace"))

ingress = Ingress(
    "ingress",
    spec= {
        "rules":[{
            "host": hostname,
            "http":{
                "paths": [{
                    "path": "/nginx-test",
                    "backend":{
                        "serviceName": service.metadata["name"],
                        "servicePort": 80
                    }
                }]
            }
        }]
    }
    )

pulumi.export("name", deployment.metadata["name"])
pulumi.export("url", ingress.spec.apply(lambda s: s['rules'][0]['host'] + s['rules'][0]['http']['paths'][0]['path'] ))
pulumi.export("password", password.result)
