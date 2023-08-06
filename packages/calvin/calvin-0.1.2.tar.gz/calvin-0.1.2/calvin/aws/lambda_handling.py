def make_response(body, code=200, headers={"Content-Type": "text/html"}, base64=False):
    return {
        "body": body,
        "statusCode": code,
        "headers": headers,
        "isBase64Encoded": base64
    }

def respond_with(response):
    return lambda *args, **kwargs: response
