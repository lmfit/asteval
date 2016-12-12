
METADATA = {
    'userMetaData': {
        'orgTCType': 0,
        'tCType': 0,
    }
}

print(METADATA)

def foo():
    METADATA['userMetaData']['orgTCType'] = 1
    METADATA['userMetaData']['tCType'] = 2
    return True

foo()
print(METADATA)

