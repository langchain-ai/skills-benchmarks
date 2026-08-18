Resize large images with sharp before sending.

```typescript
// Problem: Image exceeds size limit
const hugeImage = fs.readFileSync("./10mb_image.jpg");
// Model may reject

// Solution: Resize or compress images first
import sharp from "sharp";

const resized = await sharp("./10mb_image.jpg")
  .resize(1024, 1024, { fit: "inside" })
  .jpeg({ quality: 80 })
  .toBuffer();
```
