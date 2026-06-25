Resize large images with PIL before sending.

```python
# Problem: Image exceeds size limit
with open("./10mb_image.jpg", "rb") as f:
    huge_image = f.read()  # Too large

# Solution: Resize images first
from PIL import Image
import io

img = Image.open("./10mb_image.jpg")
img.thumbnail((1024, 1024))
buffer = io.BytesIO()
img.save(buffer, format="JPEG", quality=80)
resized_data = base64.b64encode(buffer.getvalue()).decode()
```
