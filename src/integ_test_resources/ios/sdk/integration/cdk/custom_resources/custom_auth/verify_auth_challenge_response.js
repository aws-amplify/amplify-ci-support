function verifyAuthChallengeResponse(event) {
    if (event.request.privateChallengeParameters.answer === event.request.challengeAnswer) {
        event.response.answerCorrect = true;
    } else {
        event.response.answerCorrect = false;
    }
}

exports.handler = (event, context, callback) => {
    verifyAuthChallengeResponse(event);
    callback(null, event);
};
