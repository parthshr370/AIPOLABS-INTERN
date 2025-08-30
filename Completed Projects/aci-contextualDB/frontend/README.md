# Contextual Database Chrome Extension

A Chrome extension that extracts and stores webpage content using advanced content processing.

## Quick Setup

1. **Install dependencies:**
   ```bash
   pnpm install
   # or npm install
   ```

2. **Build the extension:**
   ```bash
   pnpm run build
   # or npm run build
   ```

3. **Load in Chrome:**
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `dist` folder
   - Pin the extension to your toolbar

## Development

- `pnpm run build` - Build for production
- `pnpm run dev` - Start development server
- `pnpm run lint` - Check code quality