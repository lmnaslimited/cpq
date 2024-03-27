<div align="center">
    <picture>
        <source media="(prefers-color-scheme: light)" srcset="https://crmdocs.frappe.cloud/files/Group%201344CRMLogoWhite.png">
        <img src="https://crmdocs.frappe.cloud/files/Group%201342CRMLogo.png" height="50">
    </picture>
    <p align="center" style="font-weight: bold;">Modern, open-source, CRM solution to supercharge your sales operations.</p>
    
<img width="1402" alt="Screenshot 2022-09-18 at 9 16 08 PM" src=".github/screenshots/Deal.png">
<img width="1402" alt="Screenshot 2022-09-18 at 9 18 17 PM" src=".github/screenshots/Leads.png">
<img width="1402" alt="Screenshot 2022-09-18 at 11 47 06 PM" src=".github/screenshots/Lead.png">
<img width="1402" alt="Screenshot 2022-09-18 at 9 18 47 PM" src=".github/screenshots/Notes.png">
<img width="1402" alt="Screenshot 2022-09-18 at 9 18 47 PM" src=".github/screenshots/Call Logs.png">

</div>

# Frappe CRM

Frappe CRM is modern, open-source, CRM solution to supercharge your sales operations.

## Key Features

- **Views:** Create custom views which is a combination of filters, sort and columns.
    - **Pinned View:** Pin important leads and deals in the sidebar.
    - **Public View:** Share views to all users.
    - **Saved View:** Save views for later use.
- **Email Communication:** Send and receive emails directly from the Lead/Deal Page.
- **Email Templates:** Create and use email templates for faster communication.
- **Comments:** Add comments to leads and deals to keep track of the conversation.
- **Notifications:** Get notified when someone mentions you in a comment.
- **Service Level Agreement:** Set SLA for leads and deals and get notified when the SLA is breached.
- **Assignment Rule:** Automatically assign leads and deals to users based on the criteria.
- **Tasks:** Create tasks for leads and deals.
- **Notes:** Add notes to leads and deals.
- **Call Logs:** See the call logs with call details and recording.
- **Twilio Ingegration:** Integrate Twilio to make and receive calls from the CRM.

## Getting Started

### Self-hosting

If you prefer self-hosting, follow the official [Frappe Bench Installation](https://github.com/frappe/bench#installation) instructions.

## Want to Just Try Out or Contribute?

### Codespaces

1. Open [this link](https://github.com/codespaces/new?hide_repo_select=true&ref=master&repo=587413812&skip_quickstart=true&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=SoutheastAsia) and click on "Create Codespace".
2. Wait for initialization (~15 mins).
3. Run `bench start` from the terminal tab.
4. Click on the link beside "8000" port under "Ports" tab.
5. Log in with "Administrator" as the username and "admin" as the password.
6. Go to `<random-id>.github.dev/crm` to access the crm interface.

### Local Setup

1. [Install Bench](https://github.com/frappe/bench).
2. Install Frappe CRM app:
    ```sh
    $ bench get-app crm
    ```
3. Create a site with the crm app:
    ```sh
    $ bench --site sitename.localhost install-app crm
    ```
4. Open the site in the browser:
    ```sh
    $ bench browse sitename.localhost --user Administrator
    ```
5. Access the crm page at `sitename.localhost:8000/crm` in your web browser.

## Need help?

Join our [telegram group](https://t.me/frappecrm) for instant help.

## License

[GNU Affero General Public License v3.0](LICENSE)