import json

ECHO_EVENT_VERSION = 3


def handler(event, context):

    print('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': json.dumps('{{echoEventVersion: {}}}'.format(ECHO_EVENT_VERSION)),
        'isBase64Encoded': False
    }

def isProxyRequest(event):
    return True