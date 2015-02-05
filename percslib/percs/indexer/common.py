import hashlib

utf8 = 'utf-8'

def get_content_hash(contents):
    if isinstance(contents, unicode):
        contents = contents.encode('utf-8')
    elif isinstance(contents, str):
        contents = contents.decode('ascii', 'ignore')
    try:
        digest = hashlib.sha256(contents)
    except:
        raise
    return unicode(
        digest.hexdigest(),
        utf8
    )

