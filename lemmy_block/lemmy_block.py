"""Main program to run. Blocks communities"""
import configparser
import os
import sys
from pathlib import Path
from time import sleep

from account import Account
from instance import Instance
from block_community import BlockCommunity

from plemmy import LemmyHttp
from plemmy.responses import ListCommunitiesResponse


def check_config_file(config_file_path: Path) -> None:
    """Check to make sure a config file exists

    Args:
        config_file_path (Path): Path to a config file
    """
    if not config_file_path.is_file():
        print(f'File "{config_file_path}" is not a file')
        sys.exit(1)

    print(f'File "{config_file_path}" is a file')


def get_accounts(config_file: Path) -> list[Account]:
    """Get the accounts listed in the accounts config file

    Args:
        config_file (Path): Path to the accounts config file

    Returns:
        list[Account]: List of Account objects
    """
    config = configparser.ConfigParser(interpolation=None)
    read = config.read(config_file)

    if not read:
        print("No file, exiting")
        sys.exit(1)

    accounts: list[Account] = []

    for item in config.sections():
        items = dict(config.items(item))
        account = Account(
            account=item,
            site=items["site"],
            user=items["user"],
            password=items["password"],
        )
        accounts.append(account)

    return accounts


def get_all_communities_from_instance(instance: str) -> list[BlockCommunity]:
    """Get all the communities of an instance to block

    Args:
        instance (str): Instance url. IE: lemmy.ml

    Returns:
        list[BlockCommunity]: List of BlockCommunity objects
    """
    srv = LemmyHttp(f"https://{instance}")
    block_list: list = []
    run: int = True
    page: int = 1

    print(f"Gathering Communities from {instance}. This could take a while...")
    while run:
        try:
            print(f"Retrieving {instance} communities from Page {page}")
            # Can only retrieve 50 communities per page at a time
            api_response = srv.list_communities(limit=50, page=page, type_="Local")
            response = ListCommunitiesResponse(api_response)

            if len(response.communities) == 0:
                print("No more communities to get")
                run = False
            else:
                for community in response.communities:
                    block_list.append(
                        BlockCommunity(
                            name=community.community.name,
                            instance=instance,
                        )
                    )

                page += 1
                sleep(0.25)

        except Exception as exception:  # pylint: disable=broad-except
            run = False
            print("Issue gathering communities")
            print(f"Exception: {exception}")

    return block_list


def get_block_list(config_file: Path) -> list[BlockCommunity]:
    """Get all the communities to block for all supplied instances

    Args:
        config_file (Path): Path to instance config file

    Returns:
        list[BlockCommunity]: List of BlockCommunity objects
    """
    config = configparser.ConfigParser(interpolation=None)
    read = config.read(config_file)

    block_list: list = []

    if not read:
        print("No file, exiting")
        sys.exit(1)

    for item in config.sections():
        items = dict(config.items(item))
        block_list += get_all_communities_from_instance(items["instance"])

    return block_list


def block_communities(
    instances: list[Instance], block_list: list[BlockCommunity]
) -> None:
    """Block the communities

    Args:
        instances (list[Instance]): List of Instance Objects
        block_list (list[BlockCommunity]): List of BlockCommunity Objects
    """
    total_count: int = len(block_list)
    print(f"Number of communities to block: {total_count}")
    for instance in instances:
        try:
            print(f"Login for {instance.account.user}")
            instance.login()
            sleep(0.25)

        except Exception as exception:  # pylint: disable=broad-except
            print(f"Failed login attempt {instance.account.user}")
            print(f"Exception: {exception}")

        else:
            for index, community in enumerate(block_list):
                try:
                    print(
                        f"({index + 1}/{total_count}) Blocking"
                        f" {community.name}@{community.instance} for"
                        f" {instance.account.user}"
                    )
                    response = instance.block_community(
                        block=community.block,
                        community_id=(
                            instance.get_community(
                                f"{community.name}@{community.instance}"
                            )
                        ),
                    )
                    print(f"Community {community.name} Blocked: {response}")
                    sleep(0.25)

                except Exception as exception:  # pylint: disable=broad-except
                    print("Issue blocking communities")
                    print(f"Exception: {exception}")


def main():
    """Main section for script"""

    print("Starting lemmy_block.py")

    account_config_path = Path(os.path.dirname(__file__), "accounts.ini")
    check_config_file(account_config_path)
    block_config_path = Path(os.path.dirname(__file__), "blocklist.ini")
    check_config_file(block_config_path)

    accounts: list[Account] = get_accounts(account_config_path)

    instances: list[Instance] = []
    for account in accounts:
        instance = Instance(account=account)
        instances.append(instance)

    block_list: list = get_block_list(block_config_path)

    block_communities(instances, block_list)

    print("lemmy_block.py Complete!")


if __name__ == "__main__":
    main()
