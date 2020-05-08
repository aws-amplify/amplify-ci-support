== IoT Custom Authorizer

This is a custom resource to test IoT custom authorizers in the SDK.

It includes pregenerated resources:

- RSA Keypair used to sign and verify token values. The public key is passed to the custom resource provider's 'create' method.
- SHA256 signature generated with the following invocation: 
  `echo -n "allow" | openssl dgst -sha256 -sign custom_resources/iot_custom_authorizer_provider/iot_custom_authorizer_key.pem | openssl base64 -A`

  This value is exported to the SSM parameter store as `custom_authorizer_signature`, to remove the need for the integ test of calculating the signature

Since these resources are publicly available, they must not be used to secure resources (such as other custom IoT authorizers) in production environments.

