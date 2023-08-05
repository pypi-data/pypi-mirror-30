import json
import os

from couchutils import compile_doc

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures', 'compile_doc')
TEST_DIR = os.path.join(FIXTURES, 'test_dir')
EXPECTED = os.path.join(FIXTURES, 'expected')


def test_compile_doc():
    result = compile_doc.compile_doc(TEST_DIR)
    assert len(result) == 4

    # Test result against expected documents
    for (key, value) in result.items():
        _id = '{}.json'.format(key.split('/')[-1])  # _design/xxx
        expected = os.path.join(EXPECTED, _id)
        with open(expected, 'r') as fp:
            assert value == json.load(fp)
