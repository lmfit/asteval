metadata = {
    "a": "this is a long string XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "b": 3.1415927,
    "c": {
        "d": "this is another long string YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",
        "e": [
            "more stuff",
            "and even more"
        ]
    },
    "f": "some other long string ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
}

print(metadata)
metadata['g'] = 'test string'
print(metadata)
metadata.pop('b')
print(metadata)
