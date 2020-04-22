const IAM_PRINCIPAL_ARN = 'arn:aws:iam::<ACCOUNT_ID>:user/<USER_NAME>';
const SERVICES:string[] = ['apigateway', 'dynamodb', 'sns', 'sqs', 'ses'];

export class CdkPoliciesStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    for (var service of SERVICES) {
      const role = new iam.Role(this, service + 'Role', {
        assumedBy: new iam.ArnPrincipal(IAM_PRINCIPAL_ARN)
      });

      role.addToPolicy(new iam.PolicyStatement({
        resources: ['*'],
        actions: [ service + ‘😘'] }));

      new SSM.StringParameter(this, service + 'Param', {
        parameterName: service,
        description: 'Parameter containing role arn for ' + service,
        stringValue: role.roleArn
      })
    }
  }
}