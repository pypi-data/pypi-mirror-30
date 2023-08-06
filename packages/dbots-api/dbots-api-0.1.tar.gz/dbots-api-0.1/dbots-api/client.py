import requests

class Client:
  """Client instance for interacting with the bots.discord.pw API.
  Parameters
  ----------
  token: str
    The bots.discord.pw API auth token.
  """
  
  def __init__(self, token: str):
    self.token = token
    self.url = "https://bots.discord.pw/api"
    self.headers = { "Authorization": self.token }

  def get_user(self, user_id: int):
    """Gets information on a specific user.
    Parameters
    ----------
    user_id: int
      The ID of the user to get information about.
    """

    url = f"users/{user_id}"
    r = requests.get(f"{self.url}/{url}", headers = self.headers)
    return r

  def get_all_bots(self):
    """Gets information on all bots. (Abuse can result in an API ban.)"""

    r = requests.get(f"{self.url}/bots", headers = self.headers)
    return r
  
  def get_bot(self, bot_id: int):
    """Gets information on a specific bot.
    Parameters
    ----------
    bot_id: int
      The ID of the bot to get information about.
    """

    url = f"bots/{bot_id}"
    r = requests.get(f"{self.url}/{url}", headers = self.headers)
    return r

  def get_bot_stats(self, bot_id: int):
    """Gets statistics on a specific bot.
    Parameters
    ----------
    bot_id: int
      The ID of the bot to get statistics about.
    """

    url = f"bots/{bot_id}/stats"
    r = requests.get(f"{self.url}/{url}", headers = self.headers)
    return r

  def post_bot_stats(self, bot_id: int, keys: object):
    """Posts statistics about a specific bot.
    Parameters
    ----------
    bot_id: int
      The ID of the bot to post statistics about.
    keys: object
      The statistics of the bot to post.
    """

    url = f"bots/{bot_id}/stats"
    r = requests.post(f"{self.url}/{url}", headers = self.headers, json = keys)
    return r