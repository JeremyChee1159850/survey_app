class Reply:
    """
    Represents a reply to a message in the system.

    Attributes:
        reply_id (int): Unique identifier for the reply.
        content (str): Content of the reply.
        created_at (str): Timestamp when the reply was created.
        username (str): Username of the user who created the reply.
        avatar (str): URL or path to the avatar image of the user.
        user_id (int): ID of the user who created the reply.
    """

    def __init__(self, reply_id, content, created_at, username, avatar, user_id):
        self.reply_id = reply_id
        self.content = content
        self.created_at = created_at
        self.username = username
        self.avatar = avatar
        self.user_id = user_id
