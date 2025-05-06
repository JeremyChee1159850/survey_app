class Message:
    """
    Represents a message in the system.

    Attributes:
        message_id (int): Unique identifier for the message.
        title (str): Title of the message.
        content (str): Content of the message.
        created_at (str): Timestamp when the message was created.
        user_id (int): ID of the user who created the message.
        username (str): Username of the user who created the message.
        avatar (str): URL or path to the avatar image of the user.
    """

    def __init__(
        self, message_id, title, content, created_at, user_id, username, avatar
    ):
        self.message_id = message_id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.user_id = user_id
        self.username = username
        self.avatar = avatar
