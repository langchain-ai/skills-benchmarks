Use Playwright for SPAs:

```typescript
// Using Cheerio for dynamic content
const loader = new CheerioWebBaseLoader("https://react-app.com");
const docs = await loader.load();
// Content is empty or incomplete!

// Use Playwright for JavaScript-rendered pages
const loader = new PlaywrightWebBaseLoader("https://react-app.com", {
  gotoOptions: { waitUntil: "networkidle" }
});
```
