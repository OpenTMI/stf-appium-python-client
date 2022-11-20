import logging
import sys
import urllib
import pytest
import urllib3.exceptions
from mock import patch
from stf_appium_client.cli import main


class TestAdbServer:

    def test_help(self):
        testargs = ["prog", "--help"]
        with pytest.raises(SystemExit) as cm:
            with patch.object(sys, 'argv', testargs):
                main()
        assert cm.value.code == 0

    def test_host_invalid_requirements(self):
        testargs = ["prog", "--token", "123", "--host",
                    "http://test", "--requirements", "asdf"]
        with pytest.raises(SystemExit) as cm:
            with patch.object(sys, 'argv', testargs):
                main()
        assert cm.value.code == 1

    @patch('shutil.which')
    def test_host_not_found(self, mock_which):
        testargs = ["prog", "--token", "123", "--host", "http://test"]
        with pytest.raises(urllib3.exceptions.MaxRetryError):
            with patch.object(sys, 'argv', testargs):
                main()
