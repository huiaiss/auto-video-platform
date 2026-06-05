export default {
  async fetch(request) {
    return new Response(
      `# longjiang-ai.com — AI爬虫全开放
User-agent: *
Allow: /

# 显式允许 AI 爬虫
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: CCBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Bytespider
Allow: /

Sitemap: https://www.longjiang-ai.com/sitemap.xml
Crawl-delay: 1`,
      { headers: { "Content-Type": "text/plain" } }
    );
  }
};