# Common resources for both iOS and Android

### Device Config File Builder

`device_config_builder.py` can be used to create the contents of a
`testconfiguration.json`, as expected by the Android and iOS SDK's
integration test suites.

To use it:
```
./device_config_builder.py ios
```
Or:
```
./device_config_builder.py android
```

The script will produce a JSON structure that looks like this:
```
{
  "Credentials": {
    "accessKey": "blah",
    "secretKey": "blah",
    "sessionToken": "blah"
  },
  "Packages": {
    "pinpoint": {
      "key1": "val2"
    },
    "s3": {
      "key1": "val2"
    }
  }
}
```

The credentials are taken from the following environment variables:
  1. `AWS_ACCESS_KEY_ID`
  2. `AWS_SECRET_ACCESS_KEY`
  3. `AWS_SESSION_TOKEN`

The package data is taken from the ouputs of a call to SSM
`get-parameters-by-path`. The credentials from the environment varaibles
above are used to make the call. Only parameters that begin
`/mobile-sdk/<platform>` are considered. Parameters are expected to have
the form: `/mobile-sdk/<platform>/<suitelabel>/<keypath>`.

`<suitelabel>` is like `pinpoint` or `s3`.

`<platform>` is like `ios` or `android`.

`<keypath>` may be a simple string, or itself may be a compound like
`foo/bar/baz`. If `<keypath>` contains `/`, then the path is interpreted as a
sequence of nested JSON objects. For example, if the key path is `foo/bar`, and
the value to be stored is `value`, the JSON representation would look like:
```
"suitelabel": {
    "foo": {
        "bar": "value"
    }
}
```

------------------

[amplify.aws](https://amplify.aws)

