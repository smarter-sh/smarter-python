"""Test smarter.resources.accounts."""

from .base import SmarterTestBase


class TestAccounts(SmarterTestBase):
    """Test Accounts, Users and AccountContacts."""

    def test_accounts(self):
        """Accounts are listed and retrieved."""
        self.route("GET", "accounts/", fixture="accounts")
        self.route("GET", "accounts/1/", json_body=self.load_json("accounts")[0])
        self.assertEqual(self.client.accounts.list()[0].account_number, "1234-5678-9012")
        self.assertEqual(self.client.accounts.retrieve(1).company_name, "Example Company")

    def test_users_and_contacts(self):
        """The account's users and contacts are listed and retrieved."""
        self.route("GET", "accounts/users/", fixture="users")
        self.route("GET", "accounts/users/1/", json_body=self.load_json("users")[0])
        self.route("GET", "accounts/contacts/", fixture="contacts")
        self.route("GET", "accounts/contacts/1/", json_body=self.load_json("contacts")[0])
        self.assertTrue(self.client.accounts.users.list()[0].is_superuser)
        self.assertEqual(self.client.accounts.users.retrieve(1).username, "admin")
        self.assertTrue(self.client.accounts.contacts.list()[0].is_primary)
        self.assertEqual(self.client.accounts.contacts.retrieve(1).account.account_number, "1234-5678-9012")  # type: ignore[union-attr]

    def test_user_profiles(self):
        """The user profiles are listed and retrieved, with their users and accounts."""
        self.route("GET", "accounts/user-profiles/", fixture="user_profiles")
        self.route("GET", "accounts/user-profiles/1/", json_body=self.load_json("user_profiles")[0])
        self.assertEqual(self.client.accounts.user_profiles.list()[0].user.username, "admin")
        profile = self.client.accounts.user_profiles.retrieve(1)
        self.assertEqual(profile.account.account_number, "1234-5678-9012")
        self.assertFalse(profile.is_test)
        self.assertIsNone(profile.profile_image)

    def test_user_profile_image(self):
        """A user profile has the url of the image that the user uploaded, beside the oauth provider's."""
        body = {**self.load_json("user_profiles")[0], "profileImage": "https://example.com/uploaded.png"}
        self.route("GET", "accounts/user-profiles/1/", json_body=body)
        self.assertEqual(
            self.client.accounts.user_profiles.retrieve(1).profile_image, "https://example.com/uploaded.png"
        )
