# radleyberg-printing-press

an HTTP service to create OpenShift templates

## recommended start

```
oc new-app centos/python-35-centos7~https://github.com/elmiko/radleyberg-printing-press
oc expose svc/radleyberg-printing-press

HOST=http://`oc get routes/radleyberg-printing-press --template='{{.spec.host}}'`
curl $HOST | oc create -f -
```

want to get fancy?

```
curl $HOST/?tag=v0.3.1 | oc create -f -
```

## running tests

```
tox
```

## adding new versions and templates

`config.yaml` controls the available version with top level keys. each key
defines a template file name and a dictionary of parameters that can be
overridden through the request.

example of a new version `v1.0.0`

```
v1.0.0:
  template: resources.yaml
  parameters:
    tag: v1.0.0
```

if a new template needs to be added, it should go in the `templates` directory
and will use jinja2 template style with the variables from the `parameters`
configuration injected.

any parameters can be overridden by passing it as a query argument in the
http request.
