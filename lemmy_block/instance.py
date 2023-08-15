"""Account Class"""
from account import Account
from plemmy import LemmyHttp
from plemmy.responses import GetCommunityResponse, BlockCommunityResponse


class Instance:
    """Class for a Lemmy instance"""

    def __init__(self, account: Account) -> None:
        self.account = account
        self.srv = LemmyHttp(self.account.site)

    def login(self) -> bool:
        """Function to log into Lemmy account"""
        try:
            self.srv.login(self.account.user, self.account.password)

        except Exception as exception:  # pylint: disable=broad-except
            print(f"Unsuccessful login attempt for {self.account.user}")
            print(f"Exception: {exception}")
            return False

        print(f"Login successful for {self.account.user}")
        return True

    def get_community(self, community_name: str) -> int | None:
        """Function to get details about a community

        Args:
            community_name (str): Name of the community

        Returns:
            int: ID of the community
        """
        try:
            api_response = self.srv.get_community(name=community_name)
            response = GetCommunityResponse(api_response)
            return response.community_view.community.id

        except Exception as exception:  # pylint: disable=broad-except
            print(f"Unsuccessful get community attempt for {community_name}")
            print(f"Exception: {exception}")

        return None

    def block_community(self, block: bool, community_id: int) -> bool | None:
        """Function to block a community

        Args:
            block (bool): Block a community
            community_id (int): ID of the community

        Returns:
            bool: Returns whether the community was blocked or not
        """
        try:
            api_response = self.srv.block_community(
                block=block, community_id=community_id
            )
            response = BlockCommunityResponse(api_response)
            return response.blocked

        except Exception as exception:  # pylint: disable=broad-except
            print(
                f"Unsuccessful block attempt for user: {self.account.user} for"
                f" community id: {community_id}"
            )
            print(f"Exception: {exception}")

        return None
