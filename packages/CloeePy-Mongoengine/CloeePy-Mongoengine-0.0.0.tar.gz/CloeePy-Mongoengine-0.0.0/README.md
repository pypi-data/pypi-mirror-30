# CloeePy-Mongoengine
Mongoengine Plugin for CloeePy

Configures Mongoengine for use with CloeePy

## Installation

`pip install CloeePy-Mongoengine`

## Configuration

### Configuration Basics
CloeePy-Mongoengine configuration must be placed under `CloeePy.Plugins.cloeepy_mongoengine` in your config file.
The parameters are simply the available Mongoengine connection parameters. For more
information on possible configurations please see [Mongoengine's Documentation](https://mongoengine-odm.readthedocs.io/guide/connecting.html)

```
CloeePy:
  ...
  Plugins:
    cloeepy_mongoengine:
      alias: default
      host: "localhost"
      port: 27017
      name: myDatabase
      username: admin
      password: secret
      authentication_source: admin
      authentication_mechanism: SCRAM-SHA-1
      maxPoolSize: 100
```

### Customize Plugin Namespace

By default, your mongo connection is available on the CloeePy application context as
`app.mongoengine`. Meaning, you do have access to the underlying PyMongo Connection
instance, but you should not need to use this directly.

Optionally you can specify a different namespace by which you access
the mongo connection via `pluginNamespace`.

```
...
Plugins:
  cloeepy_mongoengine:
    pluginNamespace: customMongoengineNS
    alias: default
    host: "localhost"
    port: 27017
    name: myDatabase
    username: admin
    password: secret
    authentication_source: admin
    authentication_mechanism: SCRAM-SHA-1
    maxPoolSize: 100
```

Then, you would access your mongo connection on the application context like so:

```
app = CloeePy()
result = app.customMongoNS.admin.command("isMaster")
app.log.info(result)
```

### Optional Environment Variables

It's best practice NOT to store sensitive data, such as database usernames and passwords,
in plain-text configuration files. Thus, CloeePy-Mongoengine supports configuring your mongo username
and password via environment variables.

You need to set the following:

- Username: `CLOEEPY_MONGOENGINE_USERNAME`
- Password: `CLOEEPY_MONGOENGINE_PASSWORD`

By doing so, you can omit `username` and `password` in your configuration file.


## Usage
See [Mongoengine's Documentation](https://mongoengine-odm.readthedocs.io/guide/connecting.html)
for usage instructions.
