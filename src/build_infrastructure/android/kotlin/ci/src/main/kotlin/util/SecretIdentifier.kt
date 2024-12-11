package util

// Uniquely identifies a secret value in SecretsManager. This is a name/key pair, since SecretsManager can store
// multiple key/value pairs under each secret name
data class SecretIdentifier(
    // The secret name
    val secretName: String,
    // The key of the secret
    val secretKey: String
)
