"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = async (event) => {
    event.response.autoConfirmUser = true;
    event.response.autoVerifyEmail = true;
    return event;
};
