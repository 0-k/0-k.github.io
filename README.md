# martinklein.co

Personal website and portfolio for Martin Klein - Energy systems researcher, transmission grid planner, and creative photographer.

🌐 **Live Site**: [www.martinklein.co](https://www.martinklein.co)

## About

This is a Jekyll-based GitHub Pages site showcasing:
- Academic research and publications in energy systems analysis
- Technical blog posts on energy, programming, and data science
- Art gallery featuring analog photography manipulated with Chinese ink
- Professional experience in electricity grid planning and renewable energy integration

## Tech Stack

- **Framework**: Jekyll 4.2.0
- **Theme**: Minima (customized)
- **Hosting**: GitHub Pages
- **Analytics**: Fathom Analytics (privacy-focused)
- **Domain**: Custom domain configured via CNAME

## Project Structure

```
.
├── _posts/              # Blog posts (published and drafts)
├── _layouts/            # Custom page layouts
├── _includes/           # Reusable components (header, footer, analytics)
├── _sass/               # Custom styling
├── tag/                 # Tag archive pages
├── data/                # Images, datasets, and interactive visualizations
│   ├── hochformat/      # Portrait photos
│   ├── querformat/      # Landscape photos
│   └── cv/              # Computer vision processed images
├── open-tyndp-workshops/ # Workshop materials
├── index.md             # Home page
├── about.md             # Personal bio and experience
├── research.md          # Publications and presentations
├── blog.md              # Blog listing page
├── scratch.md           # Art gallery
├── contact.md           # Contact information
├── privacy.md           # Privacy policy
└── _config.yml          # Jekyll configuration

```

## Local Development

### Prerequisites

- Ruby (version specified in `.ruby-version` or Gemfile)
- Bundler: `gem install bundler`

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/0-k/0-k.github.io.git
   cd 0-k.github.io
   ```

2. Install dependencies:
   ```bash
   bundle install
   ```

3. Run the development server:
   ```bash
   bundle exec jekyll serve
   ```

4. Open your browser to `http://localhost:4000`

### Development Commands

- **Build site**: `bundle exec jekyll build`
- **Serve with drafts**: `bundle exec jekyll serve --drafts`
- **Serve with live reload**: `bundle exec jekyll serve --livereload`
- **Clean build files**: `bundle exec jekyll clean`

## Content Management

### Adding Blog Posts

Create a new markdown file in `_posts/` with the naming format:
```
YYYY-MM-DD-title-slug.md
```

Include front matter:
```yaml
---
layout: post
title: "Your Post Title"
tags: [energy, python, tech]
---
```

**Drafts**: Prefix filename with underscore (`_YYYY-MM-DD-title.md`) to keep unpublished.

### Adding Images

- Place images in appropriate `data/` subdirectories
- Reference in markdown: `![Alt text](/data/subfolder/image.jpg)`

### Managing Tags

- Available tags: art, energy, graphql, interview, javascript, jekyll, latex, ml, python, shopify, tech
- Tag pages are auto-generated in `tag/` directory

## Configuration

Key settings in `_config.yml`:
- Site metadata (title, description, author)
- Social media links
- Analytics configuration
- Jekyll plugins

## Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the main branch. Custom domain is configured via `CNAME` file.

## Privacy & Analytics

- Uses Fathom Analytics for privacy-respecting visitor tracking
- Includes GDPR-compliant privacy policy
- Cookie consent implementation for EU compliance

## License

Content and code © Martin Klein. All rights reserved.

## Contact

Martin Klein
📧 hi@martinklein.co
🔗 [LinkedIn](https://www.linkedin.com/in/martin-klein-)
💻 [GitHub](https://github.com/0-k)
