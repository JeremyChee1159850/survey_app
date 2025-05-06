class UserPrivacySettings:
    """
    Represents the privacy settings for a user in the system.

    Attributes:
        id (int): Unique identifier for the privacy settings.
        user_id (int): ID of the user to whom the settings belong.
        show_email (bool): Indicates whether to show the user's email.
        show_first_name (bool): Indicates whether to show the user's first name.
        show_last_name (bool): Indicates whether to show the user's last name.
        show_location (bool): Indicates whether to show the user's location.
        show_description (bool): Indicates whether to show the user's description.
        show_avatar (bool): Indicates whether to show the user's avatar.
        show_recent_post (bool): Indicates whether to show the user's recent posts.
        show_recent_vote (bool): Indicates whether to show the user's recent votes.
        show_recent_donation (bool): Indicates whether to show the user's recent donations.
    """

    def __init__(
        self,
        id,
        user_id,
        show_email,
        show_first_name,
        show_last_name,
        show_location,
        show_description,
        show_avatar,
        show_recent_post,
        show_recent_vote,
        show_recent_donation,
        show_in_user_list,
    ):
        self.id = id
        self.user_id = user_id
        self.show_email = show_email
        self.show_first_name = show_first_name
        self.show_last_name = show_last_name
        self.show_location = show_location
        self.show_description = show_description
        self.show_avatar = show_avatar
        self.show_recent_post = show_recent_post
        self.show_recent_vote = show_recent_vote
        self.show_recent_donation = show_recent_donation
        self.show_in_user_list = show_in_user_list
