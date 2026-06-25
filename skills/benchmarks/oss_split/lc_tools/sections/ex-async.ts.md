Async tool with fetch API:

```typescript
const fetchWeather = tool(
  async ({ location }: { location: string }) => {
    const response = await fetch(`https://api.weather.com/v1/location/${location}`);
    const data = await response.json();
    return `Temperature: ${data.temp}°F, Conditions: ${data.conditions}`;
  },
  {
    name: "get_weather",
    description: "Get current weather conditions for a location",
    schema: z.object({
      location: z.string().describe("City name or ZIP code"),
    }),
  }
);
```
