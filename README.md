## Telegram Bot Launcher: Setting Up and Deploying Your Telegram Bot 🚀

### Introduction 🕵️‍♂️

### 1. Configuring AWS Locally 🛠

**Using Configuration Files**:

- Go to the secret vault, typically located at `~/.aws/`.

- Make sure your configuration, `config`, contains the following:

    ```text
    [default]
    aws_access_key_id=YOUR_SECRET_ACCESS_KEY
    aws_secret_access_key=YOUR_EVEN_MORE_SECRET_KEY
    region=YOUR_PREFERRED_REGION
    ```
    Replace the placeholders with your actual AWS credentials.
  
### 2. Export the Project's Bin Directory to PATH
```bash
export PATH=$PATH:/path/to/your/project/bin
```
Replace `/path/to/your/project` with the actual path to the project on your machine.



### 3. Generating a New Project on Your Laptop 💻

Unleash your next big spy gadget (project) using:

```bash
setup_project.sh "agent-007" "<TELEGRAM_BOT_TOKEN>" --dependencies <DEPENDENCY_1> <DEPENDENCY_2> ...
```
Once it's up, proceed to add or refine your bot's business logic as required.

### 4. Running the Bot Locally 🏠

Ignite your local agent with:

```bash
run_bot.sh --no-autoreload
```
Once your gadget is set up, 🕵️‍♂️ rendezvous with your bot on Telegram.

### 5. Deploying the Bot for Your Next Mission 🌍

Before you go live, double-check the blueprints (Chalice settings) for the `TELEGRAM_BOT_ID` parameter. Don't get caught off-guard!

```json
{
  "version": "2.0",
  "app_name": "agent-007",
  "stages": {
    "dev": {
      "iam_policy_file": "dev-policy.json",
      "api_gateway_stage": "api",
      "autogen_policy": false,
      "environment_variables": {
        "TELEGRAM_BOT_ID": "6226443559:AAHtj3nUCpR89LWyKe2OWaTF3zXvtHCeeEQ"
      }
    }
  }
}

```

Deploy using:

```bash
deploy_bot.sh
```

Celebrate with your bot on Telegram post-deployment! 🎉

---
💌 Feedback and Questions

Loved the tool? Encountered a hiccup? Or simply got a suggestion? We're all ears.
Shoot an email to andrew173139@gmail.com and let's chat!
