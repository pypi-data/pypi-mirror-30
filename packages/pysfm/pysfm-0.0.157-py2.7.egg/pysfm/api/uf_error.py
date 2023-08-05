from pysfm.core.error import *

def UF_GetErrorCode(retCode):
    if retCode is UF_PROTO_RET_SCAN_FAIL:
        return UF_ERR_SCAN_FAIL
    elif retCode is UF_PROTO_RET_NOT_FOUND:
        return UF_ERR_NOT_FOUND
    elif retCode is UF_PROTO_RET_NOT_MATCH:
        return UF_ERR_NOT_MATCH
    elif retCode is UF_PROTO_RET_TRY_AGAIN:
        return UF_ERR_TRY_AGAIN
    elif retCode is UF_PROTO_RET_TIME_OUT:
        return UF_ERR_TIME_OUT
    elif retCode is UF_PROTO_RET_MEM_FULL:
        return UF_ERR_MEM_FULL
    elif retCode is UF_PROTO_RET_EXIST_ID:
        return UF_ERR_EXIST_ID
    elif retCode is UF_PROTO_RET_FINGER_LIMIT:
        return UF_ERR_FINGER_LIMIT
    elif retCode is UF_PROTO_RET_UNSUPPORTED:
        return UF_ERR_UNSUPPORTED
    elif retCode is UF_PROTO_RET_INVALID_ID:
        return UF_ERR_INVALID_ID
    elif retCode is UF_PROTO_RET_TIMEOUT_MATCH:
        return UF_ERR_TIMEOUT_MATCH
    elif retCode is UF_PROTO_RET_BUSY:
        return UF_ERR_BUSY
    elif retCode is UF_PROTO_RET_CANCELED:
        return UF_ERR_CANCELED
    elif retCode is UF_PROTO_RET_DATA_ERROR:
        return UF_ERR_DATA_ERROR
    elif retCode is UF_PROTO_RET_EXIST_FINGER:
        return UF_ERR_EXIST_FINGER
    elif retCode is UF_PROTO_RET_DURESS_FINGER:
        return UF_ERR_DURESS_FINGER
    elif retCode is UF_PROTO_RET_CARD_ERROR:
        return UF_ERR_CARD_ERROR
    elif retCode is UF_PROTO_RET_LOCKED:
        return UF_ERR_LOCKED
    elif retCode is UF_PROTO_RET_ACCESS_NOT_GRANTED:
        return UF_ERR_ACCESS_NOT_GRANTED
    elif retCode is UF_PROTO_RET_EXCEED_ENTRANCE_LIMIT:
        return UF_ERR_EXCEED_ENTRANCE_LIMIT
    elif retCode is UF_PROTO_RET_REJECTED_ID:
        return UF_ERR_REJECTED_ID
    elif retCode is UF_PROTO_FAKE_DETECTED:
        return UF_ERR_FAKE_DETECTED
    elif retCode is UF_PROTO_RET_RECOVERY_MODE:
        return UF_ERR_RECOVERY_MODE
    elif retCode is UF_PROTO_RET_NO_SERIAL_NUMBER:
        return UF_ERR_NO_SERIAL_NUMBER
    else:
        return UF_ERR_UNKNOWN

if __name__ == "__main__":
    print UF_GetErrorCode(100)
