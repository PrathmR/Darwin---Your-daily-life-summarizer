# backend/app/services/jira_service.py

import requests
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("jira_service")


def is_jira_configured() -> bool:
    """Check if all required Jira settings are present."""
    return all([
        settings.JIRA_DOMAIN,
        settings.JIRA_EMAIL,
        settings.JIRA_API_TOKEN,
        settings.JIRA_PROJECT_KEY,
    ])


def _get_auth():
    """Return (email, api_token) tuple for Basic Auth."""
    return (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)


def _base_url():
    return f"https://{settings.JIRA_DOMAIN}/rest/api/3"


def search_user_by_email(email: str) -> Optional[str]:
    """
    Search for a Jira user by email and return their accountId.
    Returns None if not found or Jira is not configured.
    """
    if not is_jira_configured():
        return None

    try:
        resp = requests.get(
            f"{_base_url()}/user/search",
            params={"query": email},
            auth=_get_auth(),
            headers={"Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        users = resp.json()

        if users and len(users) > 0:
            return users[0].get("accountId")
        return None

    except Exception as e:
        logger.warning(f"Jira user search failed for {email}: {e}")
        return None


def create_issue(
    summary: str,
    description: str,
    assignee_account_id: Optional[str] = None,
) -> Optional[str]:
    """
    Create a Jira Task issue in the configured project.
    Returns the issue key (e.g. 'DAR-42') on success, None on failure.
    """
    if not is_jira_configured():
        return None

    fields = {
        "project": {"key": settings.JIRA_PROJECT_KEY},
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}],
                }
            ],
        },
        "issuetype": {"name": "Task"},
    }

    if assignee_account_id:
        fields["assignee"] = {"accountId": assignee_account_id}

    try:
        resp = requests.post(
            f"{_base_url()}/issue",
            json={"fields": fields},
            auth=_get_auth(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        issue_key = data.get("key")
        logger.info(f"✅ Jira issue created: {issue_key}")
        return issue_key

    except Exception as e:
        logger.warning(f"Jira issue creation failed: {e}")
        return None
