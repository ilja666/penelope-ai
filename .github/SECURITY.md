# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please **DO NOT** create a public GitHub issue.

Instead, please email security concerns to: [your-email@example.com]

### What to include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Security Best Practices

### For Users:

1. **Never commit `.env` files** - They contain API keys
2. **Rotate API keys regularly** - Especially if exposed
3. **Use environment variables** - Never hardcode secrets
4. **Review dependencies** - Keep them updated
5. **Use `.env.example`** - As a template, never with real keys

### For Contributors:

1. **Pre-commit hooks** - Automatically check for sensitive files
2. **Code review** - Always review for hardcoded secrets
3. **Dependency updates** - Keep dependencies secure
4. **Security scanning** - Use tools to scan for vulnerabilities

## Known Security Considerations

- API keys are stored in `.env` files (never committed)
- No hardcoded credentials in source code
- All API communication uses HTTPS
- Environment variables are used for all sensitive data
