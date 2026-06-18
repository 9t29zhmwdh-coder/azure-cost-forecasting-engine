<div align="center">
  <img src="../RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Azure Setup Guide</h1>
</div>

## Step-by-Step: App Registration and Role Assignment

### 1. Create the App Registration

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID > App registrations**
3. Select **New registration**
4. Name: `acfe-reader` (or any name you prefer)
5. Supported account types: **Accounts in this organizational directory only**
6. Click **Register**

### 2. Note the Application Identifiers

On the app registration overview page:

| Field | Environment Variable |
|---|---|
| Application (client) ID | `AZURE_CLIENT_ID` |
| Directory (tenant) ID | `AZURE_TENANT_ID` |

### 3. Create a Client Secret

1. Navigate to **Certificates and secrets > Client secrets > New client secret**
2. Set an expiry (recommended: 12 months)
3. Click **Add**
4. Copy the **Value** immediately. It will not be shown again.
5. Set this value as `AZURE_CLIENT_SECRET`

### 4. Assign the Cost Management Reader Role

1. Navigate to **Subscriptions** and select your target subscription
2. Note the **Subscription ID** and set it as `AZURE_SUBSCRIPTION_ID`
3. Select **Access control (IAM) > Add role assignment**
4. Role: **Cost Management Reader**
5. Assign access to: **User, group, or service principal**
6. Select the `acfe-reader` application registration
7. Click **Review + assign**

### 5. Configure the Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in all four values:

```
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=your-secret-value
AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 6. Verify

```bash
python cli.py run --history 30
```

If the credentials are correct, you will see a summary of the last 30 days of costs and a forecast.

## Troubleshooting

| Error | Likely Cause |
|---|---|
| `KeyError: 'AZURE_TENANT_ID'` | Environment variable not set; run `cp .env.example .env` and fill in values |
| `401 Unauthorized` | Client secret expired or incorrect; regenerate in Entra ID |
| `403 Forbidden` | Role assignment missing or not yet propagated (can take up to 10 minutes) |
| `404 Not Found` | Subscription ID incorrect |
| Empty results | No billing data in the requested date range; try a broader `--history` value |
