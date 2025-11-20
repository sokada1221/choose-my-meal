# Restaurants Menu Researcher

A CLI tool to help choose lunch by fetching restaurant ratings from Google Maps and identifying recommended menu items using Google Gemini.

## Features
- **Restaurant Search**: Finds restaurants using the Google Places API.
- **Rating Aggregation**: Displays rating and review counts.
- **Menu Recommendations**: Uses Gemini AI to analyze reviews and extract signature or recommended dishes.
- **Sorting**: Automatically sorts results by restaurant rating.

## Prerequisites
- Python 3.x
- **Google Maps Platform API Key** (Places API enabled)
- **Google Gemini API Key**

## Getting API Keys

### Google Maps Platform API Key
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Navigate to **APIs & Services > Library**.
4.  Search for and enable **"Places API (New)"** (or "Places API").
5.  Go to **APIs & Services > Credentials**.
6.  Click **Create Credentials > API Key**.
7.  (Optional but recommended) Restrict the key to "Places API".

### Google Gemini API Key
1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Click on **"Get API key"** in the sidebar.
3.  Click **"Create API key"** (you can create it in a new or existing Google Cloud project).

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**:
    -   Copy the example file:
        ```bash
        cp .env.example .env
        ```
    -   Edit `.env` and add your API keys:
        ```
        GOOGLE_MAPS_API_KEY=your_google_maps_key
        GEMINI_API_KEY=your_gemini_key
        ```

## Usage

Run the main script:
```bash
python main.py
```

Follow the prompts to enter a list of restaurant names (comma-separated).

**Example Input:**
```
Joe's Pizza, Sushi Nakazawa, The Halal Guys
```

## Cost & Limits
-   **Google Maps Platform**: Uses the "Place Details (New)" API. Specifically, fetching reviews triggers the **"Enterprise + Atmosphere"** SKU, which has a **free monthly limit of 1,000 requests**.
-   **Google Gemini API**: The Free Tier (via Google AI Studio) provides ample quota (e.g., 15 RPM) for this tool's usage.

## Billing Safety
To ensure you are never charged unexpectedly:

1.  **Set Budgets & Alerts**:
    -   Go to **Billing > Budgets & alerts** in the Google Cloud Console.
    -   Create a budget (e.g., $1.00) and set it to email you if spending exceeds a percentage of that amount.

2.  **Set Quotas (Caps)**:
    -   Go to **APIs & Services > IAM & Admin > Quotas**.
    -   Filter for "Places API".
    -   **Recommended Cap**: Set "Requests per day" to **30**.
        -   *Reasoning*: The "Place Details (Atmosphere)" SKU (triggered by fetching reviews) has a free monthly limit of **1,000 requests**.
        -   30 requests/day * 30 days = 900 requests, which keeps you safely within the free tier.
    -   For Gemini, the Free Tier for **gemini-flash-latest** has **no daily request limit** and generous rate limits (e.g., 15 RPM), which is plenty.
