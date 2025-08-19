## Description

Brief description of changes made in this PR.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] CCXT compatibility improvement
- [ ] MockExchange integration enhancement

## Checklist

- [ ] My code follows the project's style guidelines (Ruff formatting)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules
- [ ] CCXT compatibility is maintained (if applicable)
- [ ] MockExchange API compatibility is maintained (if applicable)

## Testing

- [ ] Unit tests pass: `make test`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] Code formatting applied: `make format`
- [ ] Integration tests pass (if applicable): `make test-integration`
- [ ] Build succeeds: `make build-poetry`

## Documentation

- [ ] README.md updated (if needed)
- [ ] CHANGELOG.md updated with new entries under [Unreleased]
- [ ] API documentation updated (if applicable)
- [ ] Examples updated (if applicable)
- [ ] MockExchange compatibility documented (if applicable)

## CCXT Compatibility

- [ ] Method signatures match CCXT standards
- [ ] Return data structures follow CCXT conventions
- [ ] Error handling uses CCXT-style exceptions
- [ ] Order statuses are CCXT-compatible
- [ ] Capabilities (`exchange.has`) are accurate

## MockExchange Integration

- [ ] MockExchange API endpoints are correctly mapped
- [ ] Order status mapping is implemented (MockExchange → CCXT)
- [ ] Ticker data conversion is CCXT-compatible
- [ ] Balance operations work correctly
- [ ] Error handling for MockExchange-specific issues

## Additional Notes

Any additional information that reviewers should know about this PR.

### Breaking Changes

If this PR includes breaking changes, please describe:
- What changed
- Why it changed
- How to migrate existing code

### Performance Impact

- [ ] No performance impact
- [ ] Performance improvement
- [ ] Performance regression (explain below)

### Security Considerations

- [ ] No security implications
- [ ] Security improvement
- [ ] Security concern (explain below)

## Related Issues

Closes #(issue number)
Related to #(issue number)
