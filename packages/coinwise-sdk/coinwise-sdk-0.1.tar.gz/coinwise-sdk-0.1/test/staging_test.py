import unittest

from coinwise import CoinWise
from . import staging_test_confs


class CoinWiseIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.confs = staging_test_confs
        username = self.confs.USERNAME
        password = self.confs.PASSWORD
        client_id = self.confs.CLIENT_ID
        instance_id = self.confs.INSTANCE_ID
        self.coinwise = CoinWise(
            username=username, password=password, client_id=client_id, instance_id=instance_id
        )

    def test_login(self):
        response = self.coinwise.login()
        expected_response = {'name': 'Inflr', 'coin': 'BTC'}
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json())


if __name__ == '__main__':
    unittest.main()
