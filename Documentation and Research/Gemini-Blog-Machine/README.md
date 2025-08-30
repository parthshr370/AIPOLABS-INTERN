# 🚀 Gemini Blog Machine

An intelligent, AI-powered blog creation system that guides you through a structured workflow to produce high-quality, SEO-optimized blog posts using the Gemini CLI.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Workflow](#workflow)
- [Features](#features)
- [Example Outputs](#example-outputs)
- [Contributing](#contributing)

## 🎯 Overview

Gemini Blog Machine is a structured workflow system that works with the [Gemini CLI](https://github.com/google-gemini/gemini-cli) to help you create professional blog posts. It provides a guided, conversational approach to content creation with built-in SEO optimization and quality control.

### Key Benefits:
- **Structured Approach**: Proven workflow from ideation to publication
- **Works with Gemini CLI**: Leverages Google's official command-line AI tool
- **SEO-Optimized**: Built-in research and optimization
- **Quality Control**: Automated review and improvement suggestions
- **Flexible**: Core features by default, advanced options on demand

## 📋 Prerequisites

- **Node.js 20 or higher** - [Download here](https://nodejs.org/en/download)
- **Gemini CLI** - We'll install this in the next step

## 📦 Installation

### 1. Install Gemini CLI

Choose one of these methods:

**Option A: Run directly (no installation)**
```bash
npx https://github.com/google-gemini/gemini-cli
```

**Option B: Install globally**
```bash
npm install -g @google/gemini-cli
```

### 2. Clone this repository
```bash
git clone https://github.com/your_user_id/Gemini-Blog-Machine
cd Gemini-Blog-Machine
```

### 3. Set up authentication

**For personal use (recommended for getting started):**
- Run `gemini` and sign in with your Google account when prompted
- This gives you 60 requests/minute and 1,000 requests/day

**For API key use:**
```bash
# Get API key from https://aistudio.google.com/apikey
export GEMINI_API_KEY="your_api_key_here"
```

## 🚀 Quick Start

1. **Navigate to the project directory:**
   ```bash
   cd Gemini-Blog-Machine
   ```

2. **Start the Gemini CLI:**
   ```bash
   gemini
   ```

3. **The system will automatically greet you and start the workflow:**
   - "Hello! What do you want to blog about today?"

4. **Follow the conversational workflow:**
   - Answer questions about your topic, audience, and style
   - Say "Proceed to reference" when ready to move forward
   - Say "Proceed to style" to generate configuration
   - Say "Proceed to blog" to create your blog post
   - Say "Review blog" for quality checks

## 🔄 How It Works

The Gemini Blog Machine uses the `GEMINI.md` file as an instruction set for the Gemini CLI. When you run `gemini` in this directory, it automatically loads these instructions and guides you through a structured workflow.

**Workflow stages:**
```
Discussion → SEO Check → Reference → Style → Generate → Review → Publish
```

**Files created during the process:**
- `style.json` - Your blog configuration
- `[slug].md` - Your generated blog post
- `review.json` - Quality review criteria
- `research.md` - Research findings (optional)

## 📝 Workflow

### 1. Discussion Phase
Interactive questions about:
- Topic and main idea
- Target audience
- Preferred style and tone
- SEO keywords
- Code examples (for tutorials)

### 2. SEO Research
- Quick search for existing content
- Keyword optimization
- Content gap analysis

### 3. Reference Gathering
- Option to use reference materials
- Fact-checking resources
- Technical documentation

### 4. Style Configuration
Generates `style.json` with your preferences:
```json
{
  "blogTitle": "Your Blog Title",
  "audience": "beginners",
  "tone": "conversational",
  "structure": {
    "hookType": "question",
    "sections": [...]
  }
}
```

### 5. Blog Generation
- Creates original content
- Adds visual placeholders
- Formats code blocks
- Maintains consistent voice

### 6. Review & Polish
- Automated quality checks
- SEO verification
- Improvement suggestions

## ✨ Features

### Core Features
- Interactive content planning
- SEO research and optimization
- Structured content generation
- Automated quality review
- Support for technical tutorials
- Visual element planning

### Advanced Features (Optional)
- Deep competitor analysis
- Detailed content briefs
- Audience persona development
- Enhanced fact-checking
- Multi-format support

## 📄 Example Outputs

### Generated Blog Structure
```markdown
# Your Blog Title

Hook question or statement...

## Main Section
Content with examples and explanations...

![Image: Descriptive placeholder](placeholder)

```javascript
// Code example
const example = "with explanations";
```

## Conclusion
Call-to-action and summary...
```

### Sample Templates
Check the `templates/` directory:
- `reference.md` - Template for research materials
- `example.md` - Sample blog post structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **This Project**: [https://github.com/your_user_id/Gemini-Blog-Machine](https://github.com/your_user_id/Gemini-Blog-Machine)
- **Gemini CLI**: [https://github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)
- **Get API Key**: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

**Ready to create amazing content? Just run `gemini` in this directory and let's get started! 🚀**
