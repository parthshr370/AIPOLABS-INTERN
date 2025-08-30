# CAMEL AI Cookbook Generator Frontend

A modern React/Next.js frontend for the CAMEL AI Cookbook Generator - an intelligent system that automatically generates technical cookbooks from source code using advanced multi-agent AI.

## Features

- **Multi-Agent Visualization**: Real-time progress tracking of CAMEL AI agents
- **Code Input**: Syntax-highlighted code editor with multiple language support
- **Real-time Streaming**: Live updates during cookbook generation process
- **Style-Based Generation**: Provide an example cookbook to define the tone, and structure of the output.
- **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## CAMEL AI Integration

The frontend provides an intuitive interface for CAMEL AI's multi-agent system:

- **Style Designer Progress**: See the AI analyze your example and define the cookbook's style.
- **Planner Agent Progress**: Visual feedback during code analysis and planning
- **Writer Agent Status**: Real-time updates as content is generated
- **Assembler Agent Activity**: Live tracking of final document assembly
- **Agent Communication**: Transparent view into the multi-agent workflow

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Code Editor**: Monaco Editor (VS Code engine)
- **State Management**: React hooks
- **Streaming**: Server-Sent Events (SSE)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running (CAMEL AI Cookbook Generator)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Environment Setup

Create a `.env.local` file (if needed for additional configuration):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Project Structure

```
cookbook-frontend/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page
├── components/            # React components
│   ├── cookbook-generator.tsx  # Main generator component
│   ├── theme-provider.tsx     # Theme configuration
│   └── ui/               # shadcn/ui components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
└── public/              # Static assets
```

## Usage

1. **Input Code**: Paste your source code into the syntax-highlighted editor
2. **Provide Guidance**: Add instructions about the cookbook's purpose and audience
3. **Set the Style**: Paste an example of a well-written cookbook or document to set the style.
4. **Generate**: Click "Generate Cookbook" to start the CAMEL AI process
5. **Monitor Progress**: Watch real-time updates from each AI agent
6. **Download**: Save the generated cookbook in markdown format

## CAMEL AI Agent Workflow

The frontend visualizes the complete CAMEL AI workflow:

1. **Styling Phase**: Style Designer Agent analyzes the example to create a style guide.
2. **Planning Phase**: Planner Agent analyzes code structure based on the style.
3. **Writing Phase**: Writer Agent generates content for each section adhering to the style.  
4. **Assembly Phase**: Assembler Agent combines and polishes the final document.

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Contributing

This frontend demonstrates modern React patterns integrated with CAMEL AI's multi-agent system. Contributions welcome!

## License

MIT License 