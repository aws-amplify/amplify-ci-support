## IoT Custom Enhanced Authorizer

This is a custom resource to test IoT custom authorizers in the SDK.

IoT Custom Authorizers use a Lambda to provide an authorization decision and a policy statement for an incoming IoT request.

IoT clients provide an authorization token in the specified HTTP header field, and a signature of that token.

The IoT gateway validates the signature with the public key used to create the custom authorizer, and invokes the authorizer if the signature is valid.

In this stack, the authorizer is created using an asymmetric key created in KMS. The custom authorizer provider uses the public key provided by the `iot_custom_authorizer_key_provider` (see that README for details).

Finally, we use create & update domain configuration to get an endpoint to achieve the enhanced payload in our lambda.  Note that this is only while this feature is in beta, and should not be required at a later point in time.