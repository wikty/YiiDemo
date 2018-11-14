<?php

namespace app\common;

class ConstCode {

    // Success
    const ERROR_OK = 0;

    // Unknown error
    const ERROR_UNKNOWN = -1;

    // Error 1xx: bad request
    const ERROR_INVALID = 100;
    const ERROR_PARAM_NOT_SET = 101;

    // Error 2xx: user info incorrect
    const ERROR_USERNAME_INCORRECT = 200;
    const ERROR_PASSWORD_INCORRECT = 201;
    const ERROR_USER_NOT_EXIST = 202;
    const ERROR_USER_EXISTED = 203;
    const ERROR_USERNAME_ILLEGAL = 204;
    const ERROR_TOKEN_INVALID = 205;

    // Error 3xx: server internal error
    const ERROR_TYPE_INVALID = 300;
    const ERROR_MODEL_ERROR = 301;
}