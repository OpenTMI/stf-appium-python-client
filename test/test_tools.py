import json
import pytest
from stf_appium_client.tools import find_free_port, parse_requirements


class TestTools:

    def assertEqual(self, value1, value2):
        assert value1 == value2

    def test_port(self):
        for i in range(10):
            port = find_free_port()
            assert isinstance(port, int)

    def test_parse_requirements(self):
        self.assertEqual(parse_requirements("test=1"), {"test": "1"})
        self.assertEqual(parse_requirements(""), {})
        self.assertEqual(parse_requirements({}), {})

        req = {"test": {"a": "1"}}
        self.assertEqual(parse_requirements(json.dumps(req)), req)
        self.assertEqual(parse_requirements("test.a=1"), req)
        self.assertEqual(parse_requirements("test.a=1"), req)
        self.assertEqual(parse_requirements("test.a.b=1"), {"test": {"a": {"b": "1"}}})

        with pytest.raises(ValueError):
            self.assertEqual(parse_requirements("key="), {})
        with pytest.raises(ValueError):
            self.assertEqual(parse_requirements("="), {})
