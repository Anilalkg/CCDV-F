# Anthropic API Setup & Configuration Guide

This repository contains Python scripts and exercises for the **Claude Certified Developer – Foundations (CCDV-F)** preparation workspace.

Follow the instructions below to configure your environment variables and obtain an Anthropic API key to run the scripts.

---

## Prerequisites

- Python 3.10+
- Virtual environment configured (`.venv`)
- Installed dependencies: `anthropic`, `python-dotenv`

---

## Step 1: Obtain an Anthropic API Key

1. **Sign Up / Log In:** Go to the [Anthropic Console](https://console.anthropic.com/).
2. **Setup Billing:**
   - Navigate to **Plans & Billing**.
   - Add a credit card or payment method.
   - Initial deposit requirement starts at **$5.00 USD** (granting instant access to API usage credits).
3. **Generate Key:**
   - Go to **API Keys** in the settings menu.
   - Click **Create Key**, assign a name (e.g., `ccdv-f-dev`), and copy the generated secret string (starts with `sk-ant-api03-...`).

> **Security Note:** Never commit your API key directly into source code or push it to public repositories.

---

## Step 2: Configure Environment Variables

1. In the root directory of this project (`C:\AKG\Claude-Cert\cert-code\`), create a file named `.env`.
2. Add your API key using the standard variable name recognized by the Anthropic SDK:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your_actual_key_here
```
