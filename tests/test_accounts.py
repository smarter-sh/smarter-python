"""Test smarter.resources.accounts."""

from smarter.core.exceptions import NotFoundError, RateLimitError

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
        account = self.client.accounts.contacts.retrieve(1).account
        self.assertEqual(account.account_number, "1234-5678-9012")  # type: ignore[union-attr]

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

    def test_usage(self):
        """The user's token usage is read for a window, by default the last 24 hours."""
        self.route("GET", "accounts/usage/", fixture="token_usage")
        usage = self.client.accounts.usage("7_days")
        self.assertEqual(dict(self.last_request.url.params), {"periodicity": "7_days"})
        self.assertEqual((usage.periodicity, usage.period), ("7_days", "day"))
        self.assertEqual(len(usage.points), 7)
        self.assertEqual(usage.points[0].total_tokens, 52394)
        self.assertIsNotNone(usage.points[0].period_start.tzinfo)
        self.client.accounts.usage()
        self.assertEqual(dict(self.last_request.url.params), {"periodicity": "24_hours"})


class TestDataExports(SmarterTestBase):
    """Test DataExports."""

    def test_overview(self):
        """The overview says where the link goes, and the limits."""
        self.route("GET", "accounts/data-exports/", fixture="data_export_overview")
        overview = self.client.accounts.data_exports.overview()
        self.assertEqual(overview.email, "user@example.com")
        self.assertEqual((overview.link_hours, overview.exports_per_day, overview.exports_left_today), (24, 5, 5))
        self.assertIsNone(overview.latest)

    def test_overview_latest(self):
        """The overview has the user's latest export."""
        overview = self.load_json("data_export_overview")
        overview["latest"] = self.load_json("data_export")  # type: ignore[index]
        self.route("GET", "accounts/data-exports/", json_body=overview)
        latest = self.client.accounts.data_exports.overview().latest
        self.assertEqual(latest.step, "manifests")  # type: ignore[union-attr]

    def test_start(self):
        """Start() returns the new export (202), or the one in progress (200)."""
        self.route("POST", "accounts/data-exports/", fixture="data_export", status=202)
        export = self.client.accounts.data_exports.start()
        self.assertEqual((export.id, export.status), (7, "running"))
        self.assertEqual(export.created_at.year, 2026)

    def test_start_refused_is_not_retried(self):
        """A refused export raises RateLimitError at once, whatever the client's max_retries."""
        self.route(
            "POST",
            "accounts/data-exports/",
            status=429,
            fixture="data_export_refused",
        )
        client = self.make_client(max_retries=3)
        with self.assertRaises(RateLimitError) as context:
            client.accounts.data_exports.start()
        self.assertIn("try again tomorrow", context.exception.message)
        self.assertEqual(len(self.requests), 1)

    def test_retrieve(self):
        """An export's progress is read by its id."""
        done = {
            **self.load_json("data_export"),
            "status": "succeeded",
            "step": "done",
            "expiresAt": "2026-11-14T15:00:00+00:00",
        }
        self.route("GET", "accounts/data-exports/7/", json_body=done)
        export = self.client.accounts.data_exports.retrieve(7)
        self.assertEqual(export.status, "succeeded")
        self.assertIsNotNone(export.expires_at)

    def test_retrieve_missing(self):
        """Another user's export, or one that does not exist, raises NotFoundError with its message."""
        self.route("GET", "accounts/data-exports/8/", status=404, json_body={"detail": "You have no data export 8."})
        with self.assertRaises(NotFoundError) as context:
            self.client.accounts.data_exports.retrieve(8)
        self.assertEqual(context.exception.message, "You have no data export 8.")
