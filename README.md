# MCP Code Generator

AI-powered MCP server generator for Puch AI using Blaxel. Generate complete, deployable MCP servers from natural language prompts.

## 🚀 Features

- **Natural Language Generation**: Describe what you want and get a complete MCP server
- **Blaxel AI Integration**: Uses Blaxel sandboxes and MorphLLM for high-quality code generation
- **Puch AI Compatible**: Generated MCPs work seamlessly with Puch AI
- **Complete Project**: Generates all necessary files including documentation and deployment configs
- **Multiple Deployment Targets**: Support for Render, Vercel, and custom deployments
- **Instant Download**: Get a zip file with your complete MCP project
- **Syntax Validation**: Basic validation ensures generated code is syntactically correct

## 🏗️ How It Works

1. **User Input**: Describe your MCP in natural language
2. **Intent Analysis**: AI analyzes your requirements 
3. **Code Generation**: Blaxel generates complete project files
4. **Validation**: Syntax and structure validation
5. **Package Creation**: All files packaged into downloadable zip
6. **Deploy & Connect**: Extract, deploy to Render and connect to Puch AI

## 📦 Generated Project Structure

Each generated MCP includes:

```
generated-mcp/
├── mcp_server.py          # Main MCP implementation
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── render.yaml           # Render deployment config
├── render_start.py       # Render startup script
├── .env.example          # Environment variables template
├── README.md             # Usage instructions
├── DEPLOYMENT.md         # Deployment guide
└── GENERATION_INFO.json  # Generation metadata
```

## 🛠️ Requirements

- Python 3.11+
- Blaxel account and API key
- MorphLLM API key
- Phone number for Puch AI validation

## ⚡ Quick Start

### 1. Environment Setup

Create a `.env` file:

```env
# Puch AI Configuration
MY_NUMBER=919876543210
AUTH_TOKEN=your_bearer_token

# Blaxel Configuration  
BL_WORKSPACE=your_workspace_name
BL_API_KEY=your_blaxel_api_key

# MorphLLM (Required for fast code generation)
MORPH_API_KEY=your_morph_api_key
MORPH_MODEL=morph-v2

# Application Configuration
DOWNLOAD_BASE_URL=https://your-app.onrender.com
```

### 2. Installation

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python mcp_generator.py
```

### 4. Connect to Puch AI

```
/mcp connect wss://run.blaxel.ai/your-workspace/functions/mcp-code-generator your_token
```

## 🎯 Usage Examples

### Generate MCPs with Natural Language

```
# Weather tracking
"Weather forecasting MCP with SMS alerts for severe weather"

# Flight search  
"Flight search with price comparison across multiple airlines"

# Crypto tracking
"Cryptocurrency portfolio tracker with price alerts"

# AI content
"Document summarizer using OpenAI with batch processing"

# Automation
"Email automation assistant with template management"
```

### Using the Tools

#### Generate MCP
```
generate_mcp("flight search with price alerts")
```

#### Get Examples
```
get_mcp_examples()
```

#### Check System Status
```
system_status()
```

## 🌐 Deployment

### Blaxel Deployment

This MCP Code Generator is designed to run on Blaxel platform:

1. **Install Blaxel CLI**: `npm install -g @blaxel/cli`
2. **Login**: `bl login your-workspace`
3. **Set Environment Variables**: Configure in Blaxel workspace
4. **Deploy**: `bl deploy`
5. **Connect**: Use the Blaxel WebSocket URL with Puch AI

### Environment Variables for Blaxel

Set these in your Blaxel workspace:

- `MY_NUMBER`: Your phone number (digits only)
- `BL_WORKSPACE`: Your Blaxel workspace name
- `BL_API_KEY`: Your Blaxel API key
- `MORPH_API_KEY`: Your MorphLLM API key
- `MORPH_MODEL`: morph-v2 (default)

## 🔧 API Reference

### Core Tools

#### `validate()`
Required by Puch AI. Returns your phone number for authentication.

#### `generate_mcp(prompt, include_database=False, deployment_target="render")`
Generate a complete MCP from natural language description.

**Parameters:**
- `prompt` (str): Describe what you want the MCP to do
- `include_database` (bool): Include database functionality
- `deployment_target` (str): "render", "vercel", or "custom"

**Returns:** Generation summary with download link

#### `get_mcp_examples()`
Get examples and inspiration for MCP generation.

#### `system_status()`
Check system configuration and status.

## 🎨 Supported MCP Types

### API Integrations
- Weather services (OpenWeatherMap, WeatherAPI)
- Flight search (Skyscanner, Amadeus)
- Financial data (Alpha Vantage, Yahoo Finance)
- Social media (Twitter, Facebook, LinkedIn)
- AI services (OpenAI, Anthropic, Google)

### Utilities
- QR code generation
- URL shortening
- File conversion
- Email automation
- SMS notifications

### Data & Analytics
- Web scraping
- Report generation
- Data analysis
- Monitoring systems

### Custom Functionality
- Describe any functionality and the AI will attempt to implement it

## 🔍 Troubleshooting

### Common Issues

**Generation fails:**
- Check Blaxel API key and workspace
- Verify MorphLLM API key
- Check internet connection

**Download link not working:**
- Links expire after 24 hours
- Regenerate the MCP if needed

**Syntax errors in generated code:**
- The system includes basic validation
- Review the generated code before deployment
- Report persistent issues

**Deployment issues:**
- Check environment variables
- Review deployment logs
- Ensure all dependencies are included

### Getting Help

1. Check the generated README.md in your MCP package
2. Review DEPLOYMENT.md for deployment-specific guidance
3. Verify all environment variables are correctly set
4. Check the system status using the `system_status()` tool

## 📊 System Requirements

### For Code Generation
- Blaxel account with API access
- MorphLLM API key
- Internet connection for API calls

### For Generated MCPs
- Python 3.11+
- Deployment platform (Render, Vercel, etc.)
- Required API keys for chosen functionality

## 🔒 Security & Privacy

- API keys are never logged or stored
- Generated code is cleaned up after download expiration
- All communication uses HTTPS
- User prompts are only stored temporarily for generation

## 📝 License

MIT License. See LICENSE file for details.

## 🤝 Contributing

This is an AI-generated codebase. Contributions welcome for:
- Bug fixes
- New API integrations
- Deployment platform support
- Documentation improvements

---

**Generated with ❤️ by MCP Code Generator**