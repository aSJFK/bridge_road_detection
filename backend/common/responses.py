"""统一 API 响应格式与异常处理"""

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status


def ok(data=None, message="success", code=200, headers=None):
    """成功响应"""
    return Response(
        {"code": code, "data": data, "message": message},
        status=code,
        headers=headers,
    )


def fail(message="error", code=400, data=None):
    """失败响应"""
    http_status = code if isinstance(code, int) and 100 <= code <= 599 else status.HTTP_400_BAD_REQUEST
    return Response(
        {"code": code, "data": data, "message": message},
        status=http_status,
    )


def custom_exception_handler(exc, context):
    """DRF 全局异常处理器：统一返回格式"""
    response = drf_exception_handler(exc, context)
    if response is None:
        # 未处理异常，交给 Django 500 处理
        return None

    data = response.data
    # 提取 DRF 校验错误信息为可读字符串
    message = "请求参数有误"
    if isinstance(data, dict):
        for _key, value in data.items():
            if isinstance(value, (list, tuple)) and value:
                message = str(value[0])
            elif isinstance(value, dict) and value:
                first = next(iter(value.values()))
                message = str(first[0] if isinstance(first, (list, tuple)) else first)
            else:
                message = str(value)
            break
    elif isinstance(data, (list, tuple)) and data:
        message = str(data[0])

    return Response(
        {"code": response.status_code, "data": None, "message": message},
        status=response.status_code,
    )
