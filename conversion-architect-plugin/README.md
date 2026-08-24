# Conversion Architect - Framer Plugin

Framer plugin for the Conversion Architect landing page design system.

## Features

- **Genome Compilation**: Extract page elements and compile them into LanderGenome format
- **Family Support**: Works with portfolio_v1 design family
- **Preview Integration**: Publish previews to Conversion Architect infrastructure
- **Design Pattern Support**: Map Framer elements to genome genes

## Development

```bash
cd conversion-architect-plugin
npm install
npm run dev
```

## Opening in Framer

1. Open Framer
2. Go to Menu → Plugins → Enable Developer Tools
3. Open the Plugins menu from toolbar
4. Click "Open Development Plugin"
5. Select "Conversion Architect"

## Integration

The plugin communicates with the Conversion Architect Python package via:

- **Local API**: `http://localhost:8000` (for genome compilation)
- **Preview URLs**: Generated preview domains for testing
- **Genome Export**: JSON format compatible with LanderGenome schema

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/genomes/compile` | POST | Compile genome from context |
| `/api/v1/genomes/{id}` | GET | Get genome by ID |
| `/api/v1/genomes/{id}/preview` | POST | Generate preview |
| `/api/v1/qa/run` | POST | Run QA audit |

## Framer API Usage

```typescript
// Get selected elements
const selection = await framer.getSelection()

// Get page structure
const nodes = await framer.getPageNodes()

// Add content to canvas
await framer.addText({ text: "Hello", name: "Text" })
await framer.addSVG({ svg: "<svg>...</svg>", name: "Logo" })
```

## Authority

- **Preview Only**: This plugin supports preview deployment only
- **No Production**: Production promotion requires separate authorization
- **QA Veto**: Genomes must pass QA before preview

## License

MIT
