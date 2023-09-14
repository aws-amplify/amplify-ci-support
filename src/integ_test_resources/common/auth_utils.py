from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from constructs import Construct

def construct_identity_pool(
    scope: Construct,
    resource_id_prefix: str,
    cognito_identity_providers: list = [],
    supported_login_providers: dict = {},
    developer_provider_name: str = None,
    **kwargs
) -> (cognito.CfnIdentityPool, iam.Role, iam.Role):

    identity_pool = cognito.CfnIdentityPool(
        scope,
        resource_id_prefix + "_identity_pool",
        allow_unauthenticated_identities=True,
        cognito_identity_providers=cognito_identity_providers,
        supported_login_providers=supported_login_providers,
        developer_provider_name=developer_provider_name,
    )

    unauth_role = kwargs.get(
        "unauth_role",
        get_default_role_for_identity_pool(
            scope=scope,
            identity_pool_id=identity_pool.ref,
            role_resource_id_prefix=resource_id_prefix,
            auth=False,
            kwargs=kwargs,
        ),
    )

    auth_role = kwargs.get(
        "auth_role",
        get_default_role_for_identity_pool(
            scope=scope,
            identity_pool_id=identity_pool.ref,
            role_resource_id_prefix=resource_id_prefix,
            auth=True,
            kwargs=kwargs,
        ),
    )

    cognito.CfnIdentityPoolRoleAttachment(
        scope,
        resource_id_prefix + "identity_pool_role_attach",
        identity_pool_id=identity_pool.ref,
        roles={"unauthenticated": unauth_role.role_arn, "authenticated": auth_role.role_arn},
    )

    return identity_pool, auth_role, unauth_role


def get_default_role_condition(identity_pool_id: str, auth: bool = True,) -> dict:
    return {
        "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool_id},
        "ForAnyValue:StringLike": {
            "cognito-identity.amazonaws.com:amr": "authenticated" if auth else "unauthenticated"
        },
    }


def get_default_role_policy(auth: bool = True, kwargs={}) -> iam.PolicyStatement:
    return kwargs.get(
        "identity_pool_{}_role_policy".format("auth" if auth else "unauth"),
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["mobileanalytics:PutEvents", "cognito-sync:*", "cognito-idenity:*"],
            resources=["*"],
        ),
    )


def get_default_role_for_identity_pool(
    scope: Construct,
    identity_pool_id: str,
    role_resource_id_prefix: str,
    auth: bool = True,
    kwargs={},
) -> iam.Role:
    role_policy = get_default_role_policy(auth=auth, kwargs=kwargs)
    role_condition = get_default_role_condition(identity_pool_id=identity_pool_id, auth=auth)
    role = iam.Role(
        scope,
        role_resource_id_prefix + ("auth" if auth else "unauth"),
        assumed_by=iam.FederatedPrincipal(
            "cognito-identity.amazonaws.com", role_condition, "sts:AssumeRoleWithWebIdentity"
        ),
    )
    role.add_to_policy(role_policy)
    return role
