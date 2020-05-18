function createAuthChallenge(event) {
    if (event.request.challengeName === 'CUSTOM_CHALLENGE') {
        event.response.publicChallengeParameters = { testKey: 'testResult' };
        event.response.privateChallengeParameters = {};
        event.response.privateChallengeParameters.answer = '1133';
    }
}

exports.handler = (event, context, callback) => {
    createAuthChallenge(event);
    callback(null, event);
};
