from rest_framework.response import Response


def success(data=None):
    ret = {
        'success': True,
        'message': 'OK!',
        'data': data,
    }
    return Response(ret)


def failed(message, data=None):
    ret = {
        'success': False,
        'message': message,
        'data': data,
    }
    return Response(ret)