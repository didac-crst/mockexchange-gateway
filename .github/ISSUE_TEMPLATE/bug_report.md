---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug']
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Environment

- **OS**: [e.g. macOS, Ubuntu, Windows]
- **Python Version**: [e.g. 3.12.0]
- **MockX Gateway Version**: [e.g. 0.2.0]
- **MockExchange Version**: [e.g. latest]
- **Mode**: [Paper/Production]

## Configuration

```python
# Your gateway configuration (remove sensitive data)
gateway = ExchangeFactory.create_paper_gateway(
    base_url="http://localhost:8000",
    api_key="dev-key"
)
```

## Error Messages

```
# Paste any error messages here
```

## Additional Context

Add any other context about the problem here.

## Checklist

- [ ] I have searched existing issues for similar problems
- [ ] I have provided all required information
- [ ] I can reproduce this issue consistently
- [ ] This is not a duplicate of an existing issue
