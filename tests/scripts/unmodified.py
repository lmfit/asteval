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
metadata['g'] = 'test string'
metadata.pop('b')
print(metadata)
metadata['c']['e'].append("more stuff 2")
metadata['c']['e'][0] = "more stuff 1"
metadata['c']['e'][0] = "more stuff 1"
print(metadata)
