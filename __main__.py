import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Namespace, Service
#from pulumi_random.random_pet import RandomPet

app_labels = { "app": "nginx" }

config = pulumi.Config()

#release = config.get('release') or RandomPet("Release").id

deployment = Deployment(
    "test-deployment",
    metadata={"namespace": config.require('namespace')},
    spec={
        "metadata": {
            "namespace": config.require('namespace')
        },
        "selector": { "match_labels": app_labels },
        "replicas": 2,
        "template": {
            "metadata": { "labels": app_labels },
            "spec": { "containers": [{ "name": "nginx", "image": "nginx" }] }
        }
    })

service = Service("service")

pulumi.export("name", deployment.metadata["name"])
