The `iot_custom_authorizer_function` is duplicated from the iOS test
resources.

Unlike the iOS tests, the Android tests created the remaining custom
resources from the client, itself.

The value of the authorization lambda ARN is provided to the client via
the configuration file, and the client builds the authorizer while
arranging the tests.


