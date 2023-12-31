CODE_SUCCESS = "00"
CODE_TOKEN_NOT_VALID = "01"
CODE_LOGIN_FAIL = "02"
CODE_ERROR_USER_CODE_NOT_FOUND = "03"
CODE_ERROR_POST_CODE_NOT_FOUND = "04"
CODE_ERROR_CANT_CHANGE_INFO = '05'
CODE_ERROR_WHEN_UPDATE_CREATE = "06"
CODE_ERROR_INPUT = "07"
CODE_ERROR_WHEN_UPDATE_CREATE_NOTI = '08'
CODE_ERROR_WHEN_UPDATE_CREATE_FRIEND_REQUEST = "09"
CODE_ERROR_WHEN_UPDATE_CREATE_USER = '10'
CODE_ERROR_FRIEND_REQUEST_NOT_FOUND = "11"

CODE_ERROR_SERVER = "99"

TYPE_MESSAGE_RESPONSE = {
    "en": {
        CODE_SUCCESS: "Success",
        CODE_TOKEN_NOT_VALID: 'Token is not valid',
        CODE_LOGIN_FAIL: "Username or password was wrong",
        CODE_ERROR_USER_CODE_NOT_FOUND: "user code not found",
        CODE_ERROR_POST_CODE_NOT_FOUND: "Post not found",
        CODE_ERROR_CANT_CHANGE_INFO: "Can't change information of other use",
        CODE_ERROR_WHEN_UPDATE_CREATE: "Got some error when update or create data",
        CODE_ERROR_INPUT:"",
CODE_ERROR_WHEN_UPDATE_CREATE_NOTI: "Got some error when create notification",
CODE_ERROR_WHEN_UPDATE_CREATE_FRIEND_REQUEST: "Got some error when create friend request",
CODE_ERROR_WHEN_UPDATE_CREATE_USER: "Got some error when create user",
        CODE_ERROR_SERVER: "Got some error",
CODE_ERROR_FRIEND_REQUEST_NOT_FOUND: "Friend request not found"
    }
}

PAGING_LIMIT = 10

FRIEND = 'friend'
NOT_FRIEND = 'not_friend'
PENDDING = 'pendding'
