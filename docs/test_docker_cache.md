# Test Docker Build Caching

## Purpose
This test verifies that Docker build caching is working correctly.

## Steps to Validate Caching

1. Run the initial build:
```bash
docker build -t test-cache -f bot/Dockerfile .
```

2. Make a small change to the application code (not requirements.txt)

3. Run the build again:
```bash
docker build -t test-cache -f bot/Dockerfile .
```

4. Verify that Docker reused cached layers for:
   - System dependencies installation
   - Python dependencies installation
   - Only rebuilt the application code layer

## Expected Behavior
- Layers before the application code copy should be reused from cache
- Only the final layers containing application code should rebuild
- Build time should be significantly reduced due to caching