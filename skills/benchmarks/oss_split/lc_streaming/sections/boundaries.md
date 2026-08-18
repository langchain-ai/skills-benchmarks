What You CAN Configure:
- **Stream modes**: Choose which data to stream
- **Multiple modes**: Combine different stream types
- **Custom updates**: Emit user-defined progress data
- **Chunk processing**: Handle each chunk as needed
- **Error handling**: Catch and handle stream errors

What You CANNOT Configure:
- **Chunk size**: Determined by model/provider
- **Chunk timing**: Arrives as provider sends
- **Guarantee order**: Async streams may vary
- **Modify past chunks**: Chunks are immutable
