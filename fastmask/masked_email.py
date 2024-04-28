from typing import Callable
import json
import requests
from datetime import datetime, timezone, timedelta


HOSTNAME = 'api.fastmail.com'
JMAP_CORE = 'urn:ietf:params:jmap:core'
MASKED_EMAIL_SCOPE = 'https://www.fastmail.com/dev/maskedemail'


class MaskedMailClient:
    """
    Client for interfacing with Fastmail's Masked Email JMAP API

    https://www.fastmail.com/developer/maskedemail/

    https://jmap.io/
    """

    def __init__(self, username: str, token: str):
        """Initialize using a username and Fastmail API token"""

        if username is not None and token is not None:
            if len(username) == 0 and len(token) == 0:
                print('No username/token found. Exiting...')
                exit()
        else:
            print('No username/token found. Exiting...')
            exit()

        self.hostname = HOSTNAME
        self.username = username
        self.token = token
        self.session = self.get_session()
        self.api_url = self.session['apiUrl']
        self.account_id = self.get_account_id()

    def get_session(self) -> dict:
        """Return the JMAP Session Resource as a Python dict

        Borrowed from Fastmail's tiny_jmap_library.py: https://github.com/fastmail/JMAP-Samples
        """

        try:
            if self.session:
                return self.session
        except:
            pass

        r = requests.get(
            "https://" + self.hostname + "/.well-known/jmap",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
        )
        r.raise_for_status()
        return r.json()

    def get_api_url(self) -> str:
        """Get API URL from session"""

        if not self.session:
            self.get_session()
        return self.session['apiUrl']

    def get_account_id(self) -> str:
        """Return the accountId for the account matching self.username


        Borrowed from Fastmail's tiny_jmap_library.py: https://github.com/fastmail/JMAP-Samples
        """
        try:
            if self.account_id:
                return self.account_id
        except:
            pass

        session = self.get_session()

        return session["primaryAccounts"][JMAP_CORE]

    def __jmap_call(self, call: dict) -> dict:
        """
        Make a JMAP POST request to the API, returning the reponse as a
        Python data structure.

        Borrowed from Fastmail's tiny_jmap_library.py https://github.com/fastmail/JMAP-Samples
        """
        res = requests.post(
            self.api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            data=json.dumps(call),
        )
        res.raise_for_status()
        return res.json()

    def get(self, ids: list[str] | None = None, filters: Callable | None = None, sort_by: str | None = None, sort_order: str = 'asc', limit: int | None = None) -> list[dict]:
        """Get Masked Emails associated with account.

        ids [optional]: Return Masked Emails matching IDs
        filters [optional]: Optionally filter list results by field (see https://www.fastmail.com/developer/maskedemail/#object for options)
        sort_by [optional]: Field to sort results by
        sort_order [optional]: Whether to sort ascending or descending. Accepted values: 'asc' or 'desc'
        limit: Number of results to return
        """

        response = self.__jmap_call({
            'using': [JMAP_CORE, MASKED_EMAIL_SCOPE],
            'methodCalls': [
                [
                    'MaskedEmail/get',
                    {
                        'accountId': self.account_id,
                        'ids': ids,
                    },
                    'a'
                ]
            ]
        })

        masked_email_list = response['methodResponses'][0][1]['list']

        if filters is not None:
            masked_email_list = list(filter(filters, masked_email_list))

        if sort_by is not None: #TODO remove items without None in sort_by?
            masked_email_list = sorted(masked_email_list, key=lambda x: (x[sort_by] is None, x[sort_by]), reverse=(sort_order == 'desc'))

        if limit is not None:
            return masked_email_list[:limit]

        return masked_email_list

    def new(self, url: str | None = None, domain: str = '', description: str = '', state: str = 'enabled'):
        'Created a new Masked Email, optionally setting url, forDomain, description'

        response = self.__jmap_call({
            'using': [JMAP_CORE, MASKED_EMAIL_SCOPE],
            'methodCalls': [
                [
                    'MaskedEmail/set',
                    {
                        'accountId': self.account_id,
                        'create': {
                            'new-masked-email': {
                                'state': state,
                                'description': description,
                                'url': url,
                                'forDomain': domain,
                            }
                        }
                    },
                    'a'
                ]
            ]
        })
        return response['methodResponses'][0]

    def update(self, masked_id: str, changes: dict) -> dict:
        """Update an existing Masked Email"""

        response = self.__jmap_call({
            'using': [JMAP_CORE, MASKED_EMAIL_SCOPE],
            'methodCalls': [
                [
                    'MaskedEmail/set',
                    {
                        'accountId': self.account_id,
                        'update': {
                            masked_id: changes,
                        }
                    },
                    'a'
                ]
            ]
        })
        return response['methodResponses'][0]

    def get_active(self) -> list[dict]:
        """Get all active Masked Emails"""

        return self.get(filters=(
            lambda x: x['state'] == 'enabled'
        ))

    def get_disabled(self) -> list[dict]:
        """Get all blocked Masked Emails"""

        return self.get(filters=(
            lambda x: x['state'] == 'disabled'
        ))

    def get_deleted(self) -> list[dict]:
        """Get all deleted Masked Emails"""

        return self.get(filters=(
            lambda x: x['state'] == 'deleted'
        ))

    def get_unused(self) -> list[dict]:
        """Get all active Masked Emails that have not received messages"""

        return self.get(filters=(
            lambda x: x['lastMessageAt'] is None and x['state'] == 'enabled'
        ))

    def enable(self, masked_id: str) -> dict:
        """Set Masked Email to active"""

        return self.update(
            masked_id=masked_id,
            changes={
                'state': 'enabled'
            }
        )

    def disable(self, masked_id: str) -> dict:
        """Set Masked Email to blocked"""

        return self.update(
            masked_id=masked_id,
            changes={
                'state': 'disabled'
            }
        )

    def delete(self, masked_id: str) -> dict:
        """
        Delete Masked Email

        Address will appear under 'Review deleted masked address' and will remain recoverable. Does not permanently delete.
        """

        return self.update(
            masked_id=masked_id,
            changes={
                'state': 'deleted'
            }
        )

    def search(self, query: str, fields: list[str] = ['email', 'description']) -> list[dict]:
        """
        Search for Masked Emails matching query text

        Defaults to searching email and description fields only.
        """

        query = query.lower()
        return self.get(filters=(
            lambda x: any(query in x[f].lower() for f in fields if x[f] is not None)
        ))

    def get_recent(self, timeframe: timedelta = timedelta(days=3)) -> list[dict]:
        """Get recently created Masked Emails (default is 3 days)"""

        t_format = "%Y-%m-%dT%H:%M:%SZ"
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        return self.get(
            filters=(
                lambda x: (now - datetime.strptime(x['createdAt'], t_format)) < timeframe
            ),
            sort_by='createdAt', sort_order='desc'
        )
