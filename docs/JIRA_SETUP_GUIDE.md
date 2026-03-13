# Jira Setup Guide for Darwin Meeting Summarizer

Darwin can automatically create tasks in your Jira Cloud project when action items are detected during meeting summarizations, and assign them directly to your team members. 

This guide will walk you through setting up a Jira Cloud instance, generating the necessary credentials, and configuring Darwin to connect to it.

## Prerequisites

- A Jira Cloud account (the Free tier is completely sufficient).
- Administrative access to create projects and manage users.

---

## Step 1: Create a Jira Free Account (If you don't have one)

1. Go to [https://www.atlassian.com/software/jira/free](https://www.atlassian.com/software/jira/free).
2. Click **Get it free**.
3. Choose "Jira Software" and click Next.
4. Sign up using your Google account or email.
5. Choose a site name (e.g., `my-startup-site`). 
   *Note: This site name will be part of your `JIRA_DOMAIN` (e.g., `my-startup-site.atlassian.net`).*

---

## Step 2: Create a Project

Once you are logged into your Jira site:

1. Click **Projects** in the top navigation bar, then select **Create project**.
2. Select the **Software development** category.
3. Choose a template (the **Kanban** or **Scrum** templates work best).
4. Select **Team-managed project** (recommended for simplicity) or **Company-managed project**.
5. Give the project a name (e.g., "Darwin Integrations").
6. Note the **Key** that is automatically generated (e.g., `DAR`). 
   *Note: This is your `JIRA_PROJECT_KEY`.*
7. Click **Create project**.

---

## Step 3: Add Your Team Members to Jira

For Darwin to assign tasks to your team members, they must exist in your Jira Cloud instance.

1. Click the **Settings (Gear Icon)** in the top right corner.
2. Select **User management**.
3. Click **Invite users**.
4. Enter the email addresses of your team members. 
5. Click **Invite**.

*Important: The email addresses you invite here MUST MATCH the email addresses you enter when adding Team Members in the Darwin frontend.*

---

## Step 4: Generate a Jira API Token

To allow Darwin to talk to Jira on your behalf, you need an API token.

1. Go directly to Atlassian Account Security: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
   *(Ensure you are logged in with the same account that created the Jira project).*
2. Click **Create API token**.
3. Give it a memorable label (e.g., "Darwin Backend").
4. Click **Create**.
5. **Copy the token immediately** using the Copy button. You will not be able to see it again after closing the window.
   *Note: This is your `JIRA_API_TOKEN`.*

---

## Step 5: Configure Darwin

You now have all the necessary information to connect Darwin to your Jira instance.

Open the `.env` file located in `backend/.env` (or wherever your environment variables for the backend are stored), and add/update the following variables:

```env
# Existing settings
# ...

# Jira Integration Settings
JIRA_DOMAIN=your-site-name.atlassian.net
JIRA_EMAIL=the_email_you_used_to_generate_the_token@example.com
JIRA_API_TOKEN=your_copied_api_token_here
JIRA_PROJECT_KEY=DAR
```

### Explanation of Variables:

- `JIRA_DOMAIN`: The domain of your Jira instance (don't include `https://`).
- `JIRA_EMAIL`: The email address of the Jira account that generated the API Token.
- `JIRA_API_TOKEN`: The secret token you generated in Step 4.
- `JIRA_PROJECT_KEY`: The 2-4 letter identifier of the project where you want issues created (from Step 2).

---

## Step 6: Test the Integration

1. Restart your Darwin backend server so it picks up the new `.env` variables.
2. Log into the Darwin frontend.
3. On the summarization page, choose **Project Manager** as your role.
4. Click **Manage Team**.
5. Add a team member using the EXACT name and email address they use in Jira. 
   *(Darwin will silently verify this email with Jira and grab their internal `accountId`).*
6. Upload a meeting transcript where that person is assigned a task.
7. Once the summarization completes, check your Jira project. A new `Task` should be created and assigned directly to that user!

### Troubleshooting

- **Task created, but unassigned:** The email address entered in Darwin's "Manage Team" modal does not match the email address in Jira, or their Jira account is disabled.
- **No Jira tasks created at all:** Ensure all 4 environment variables are present and correct. Check the backend logs for authentication errors (e.g., 401 Unauthorized usually means the API token was wrong or the email doesn't match the token owner).
