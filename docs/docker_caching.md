# Docker Caching Strategy

## Overview

Our Docker build process uses multiple caching strategies to speed up builds and reduce resource usage.

## GitHub Actions Caching

### Layer Caching
- We use GitHub Actions' built-in cache with `type=gha` for both `cache-from` and `cache-to`
- This stores Docker layers between workflow runs
- Cache is shared across different workflow runs for faster builds

### Cache Configuration
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

The `mode=max` option ensures maximum cache efficiency by storing all possible layers.

## Dockerfile Optimization

### Multi-stage Build Considerations
Our Dockerfile is optimized with the following caching principles:

1. **Dependencies First**: `requirements.txt` is copied and dependencies installed before copying source code
2. **Layer Reusability**: System dependencies are installed in a separate layer that rarely changes
3. **Cache Busting**: Using `--no-cache-dir` for pip to prevent pip's internal cache from interfering

### Dockerfile Structure
```
# System dependencies (changes rarely)
RUN apt-get update && apt-get install -y ...

# Python dependencies (changes when requirements.txt changes)
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (changes most frequently)
COPY . .
```

## Benefits

- Faster build times when only application code changes
- Reduced bandwidth usage
- Lower resource consumption on CI runners
- Consistent build environment

## When Caching Applies

Caching is most effective when:
- Only application code changes (not dependencies)
- Building similar image variants
- Running repeated builds during development

Caching will be bypassed when:
- `requirements.txt` changes
- System dependencies change
- Dockerfile changes affect earlier layers