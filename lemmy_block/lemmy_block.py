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
                    if community.community.id is not None:
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


def block_community(
    index: int, total_count: int, community: object, instance: object
) -> None:
    """Function to preform logic for blocking a community

    Args:
        index (int): Index from Block List
        total_count (int): Total number of communities from Block List
        community (object): Community Object
        instance (object): Instance Object
    """
    print(
        f"({index + 1}/{total_count}) Blocking"
        f" {community.name}@{community.instance} for"
        f" {instance.account.user}"
    )
    try:
        # Get the Community View
        community_view: object = instance.get_community(
            f"{community.name}@{community.instance}"
        )
        sleep(0.25)

        # If community is blocked, skip
        if community_view.blocked is True:
            print(f"Skipping {community.name}@{community.instance}, already blocked")
        # Block the community
        else:
            response = instance.block_community(
                block=community.block,
                community_id=(community_view.community.id),
            )
            print(f"Community {community.name} Blocked: {response}")
            sleep(0.25)

    except Exception as exception:  # pylint: disable=broad-except
        print(f"Issue blocking {community.name}@{community.instance}")
        print(f"Exception: {exception}")


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

    # Go through each instance defined
    for instance in instances:
        print(f"Attempting login for {instance.account.user}")
        result: bool = instance.login()
        sleep(0.25)

        # If account login was successful, continue
        if result is True:
            blocked_instances: list | None = None

            # Get blocked instances from account's instance
            try:
                blocked_instances = instance.get_blocked_instances()
                sleep(0.25)

            except Exception as exception:  # pylint: disable=broad-except
                print(f"Exception: {exception}")

            # Go through each community and perform logic for blocking
            for index, community in enumerate(block_list):
                # If we failed to retrieve the Federated Instance List, can't skip anything
                if blocked_instances is None:
                    print(f"Failed to gather Blocked Instances for {instance.srv}")
                    print("Will not be able to skip unnecessary blocks")

                # If we retrieved the Federated Instance List, skip needed communities
                if blocked_instances is not None:
                    if any(i.domain == community.instance for i in blocked_instances):
                        print(
                            f"({index + 1}/{total_count}) "
                            f"Skipping {community.name}@{community.instance},"
                            f" instance {community.instance} blocked from"
                            f" {instance.account.site}"
                        )
                        continue

                # Block the community
                block_community(
                    index=index,
                    total_count=total_count,
                    community=community,
                    instance=instance,
                )


def main():
    """Main section for script"""

    print("Starting lemmy_block.py")

    # Gather ini files
    account_config_path = Path(os.path.dirname(__file__), "accounts.ini")
    check_config_file(account_config_path)
    block_config_path = Path(os.path.dirname(__file__), "blocklist.ini")
    check_config_file(block_config_path)

    # Load account(s)
    accounts: list[Account] = get_accounts(account_config_path)

    # Get instance(s)
    instances: list[Instance] = []
    for account in accounts:
        instance = Instance(account=account)
        instances.append(instance)

    # Get the block list
    block_list: list = get_block_list(block_config_path)

    # Perform Blocking Logic
    block_communities(instances, block_list)

    print("lemmy_block.py Complete!")


if __name__ == "__main__":
    main()
