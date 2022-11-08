import unittest
from request.request_manager import *


class TestCreateInvite(unittest.TestCase):

    def test_create_one_invite(self):
        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=1,
            inviter_id=2,
            message_id=1,
            channel_id=0
        )
        self.assertTrue(1 in invited_users)
        self.assertTrue(2 in inviter_users)

    def test_create_more_invites(self):
        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=3,
            inviter_id=4,
            message_id=2,
            channel_id=0
        )
        self.assertTrue(3 in invited_users)
        self.assertTrue(4 in inviter_users)

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=5,
            inviter_id=8,
            message_id=20,
            channel_id=0
        )
        self.assertTrue(5 in invited_users)
        self.assertTrue(8 in inviter_users)

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=8,
            inviter_id=5,
            message_id=2022,
            channel_id=0
        )
        self.assertTrue(8 in invited_users)
        self.assertTrue(5 in inviter_users)

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=5,
            inviter_id=9,
            message_id=8,
            channel_id=0
        )
        self.assertTrue(5 in invited_users)
        self.assertTrue(9 in inviter_users)

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=32,
            inviter_id=40,
            message_id=222,
            channel_id=0
        )
        self.assertTrue(32 in invited_users)
        self.assertTrue(40 in inviter_users)

    def test_accepting_request_by_invited(self):
        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=1,
            inviter_id=2,
            message_id=1,
            channel_id=0
        )

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=3,
            inviter_id=4,
            message_id=2,
            channel_id=0
        )
        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=5,
            inviter_id=8,
            message_id=20,
            channel_id=0
        )

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=8,
            inviter_id=5,
            message_id=2022,
            channel_id=0
        )

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=5,
            inviter_id=9,
            message_id=8,
            channel_id=0
        )

        create_invite(
            invited_name='test_name',
            inviter_name='test_name',
            invited_id=32,
            inviter_id=40,
            message_id=222,
            channel_id=0
        )

        a = try_accepting_request(1, 1)
        self.assertEqual(len(a[1]), 0)

        a = try_accepting_request(3, 2)
        self.assertEqual(len(a[1]), 0)

        a = try_accepting_request(5, 20)
        self.assertEqual(len(a[1]), 2)

        a = try_accepting_request(32, 222)
        self.assertEqual(len(a[1]), 0)

        self.assertEqual(invited_users, {})
        self.assertEqual(inviter_users, {})