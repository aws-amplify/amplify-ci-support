## IoT Custom Authorizer Key

This is provider creates an asymmetric key in KMS, and uses it to pregenerate a signature for the supplied `token_value`. It returns the token signature, for use by the IoT integration tests, and the public key, which is used to create the `iot_custom_authorizer` (see that README for more details).

The signature is exported to the SSM parameter store as `custom_authorizer_token_signature`, to remove the need for the integ test to calculate the signature.
