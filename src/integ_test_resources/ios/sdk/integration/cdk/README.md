## Parameter

### emailSesIdentityArn

This parameter is the Amazon Resource Name (ARN) of the SES identity, which is utilized to dispatch email messages for the user pools of the `mobileclient` stack.

Usage example:

```
cdk deploy \
-c account=$AWS_DEV_ACCOUNT \
-c region=us-east-1 mobileclient \
--parameters mobileclient:emailSesIdentityArn='arn:aws:ses:us-east-1:<123123123123>:identity/test@example.com'
```
