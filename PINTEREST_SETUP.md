# Pinterest Integration Setup Guide

This guide explains how to set up and use the Pinterest integration feature in the Vision Board tab.

## Features

The Pinterest integration allows you to:
- **Import images from Pinterest boards** directly to your Vision Board
- **Map pins to vision board areas** automatically based on keywords
- **Connect with Pinterest API** to access private boards and pins
- **Import individual pins** or entire boards

## Setup Options

### Option 1: Simple URL Import (No Authentication Required)

You can paste Pinterest URLs directly, but this method has limitations:
- Works best with public boards
- May not work for private boards
- Requires manual image selection

**How to use:**
1. Copy Pinterest board or pin URLs
2. Paste them in the "Importar por URL" tab
3. The app will attempt to extract image information

### Option 2: Full API Integration (Recommended)

For the best experience, set up Pinterest API authentication:

#### Step 1: Create a Pinterest App

1. Go to [Pinterest Developers](https://developers.pinterest.com/apps/)
2. Click "Create app"
3. Fill in your app details:
   - App name: Your app name
   - App description: Brief description
   - Website URL: Your website or app URL
   - Redirect URI: `http://localhost:8501` (for local) or your deployed app URL
4. Note down your **App ID** and **App Secret**

#### Step 2: Configure Credentials

Create or edit `.streamlit/secrets.toml` in your project root:

```toml
[pinterest]
app_id = "your_pinterest_app_id_here"
app_secret = "your_pinterest_app_secret_here"
```

**For Streamlit Cloud:**
1. Go to your app settings on Streamlit Cloud
2. Click "Secrets"
3. Paste the same TOML format

#### Step 3: Configure Redirect URI

Make sure the Redirect URI in your Pinterest app settings matches:
- **Local development:** `http://localhost:8501`
- **Streamlit Cloud:** `https://your-app-name.streamlit.app`

#### Step 4: Authenticate

1. In the Vision Board tab, go to "Conectar com API"
2. Enter your Redirect URI
3. Click the authorization link
4. Authorize the app on Pinterest
5. Copy the authorization code from the redirect URL
6. Paste it in the app and click "Conectar"

## Usage

### Importing from a Board

1. After authentication, select a board from the dropdown
2. Click "Importar Pins do Board"
3. The app will:
   - Fetch all pins from the board
   - Automatically map them to vision board areas based on keywords
   - Show a preview of the mapping
4. Click "Adicionar ao Vision Board" to import the images

### Mapping Logic

Pins are automatically mapped to vision board areas based on:
- Pin titles
- Pin descriptions
- Keywords associated with each vision area
- Your SMART goals (if available)

You can manually reassign images after import if needed.

## Vision Board Areas

The app maps pins to these areas:
- 💼 Carreira & Projetos (Career & Projects)
- 🌿 Saúde & Bem-Estar (Health & Wellness)
- 🔮 Espiritualidade (Spirituality)
- 🦋 Crescimento Pessoal (Personal Growth)
- 💕 Amor Próprio (Self-Love)
- ✈️ Viagens & Aventuras (Travel & Adventures)
- 💰 Abundância (Abundance)
- 🎨 Criatividade (Creativity)

## Troubleshooting

### "Configuração necessária" Message

This means your Pinterest credentials are not set up. Follow Step 2 above to configure them.

### OAuth Authentication Fails

- Verify your App ID and Secret are correct
- Check that your Redirect URI matches exactly
- Ensure your app is approved (sandbox mode may have limitations)

### Images Not Importing

- Check your internet connection
- Verify the board/pin is accessible (not private or deleted)
- Try reducing the maximum number of images
- Check browser console for errors

### Rate Limiting

Pinterest API has rate limits. If you see errors:
- Wait a few minutes before retrying
- Reduce the number of pins you're importing at once
- Consider using URL import for small batches

## API Permissions Required

The integration requires these Pinterest API scopes:
- `boards:read` - To read your boards
- `pins:read` - To read pins from boards

## Privacy & Security

- Your Pinterest access token is stored in session state (temporary)
- Images are downloaded and stored locally in your app session
- No Pinterest data is shared with third parties
- You can disconnect at any time

## Limitations

- Pinterest API has rate limits (check Pinterest documentation)
- Some boards/pins may require special permissions
- Large boards may take time to process
- Image quality depends on Pinterest's original upload quality

## Support

For issues or questions:
1. Check Pinterest API documentation: https://developers.pinterest.com/docs/
2. Review Pinterest API status and limits
3. Check your app logs for detailed error messages

## Alternative: Manual Import

If API integration is not suitable, you can always:
1. Download images from Pinterest manually
2. Use the regular "Upload fotos" feature in each vision area
3. Drag and drop images directly

This gives you full control over which images to include.

