# Custom Git Commit Convention

To keep our custom enhancements clearly distinguishable from upstream MoneyPrinterTurbo commits:

## Commit Message Format
`<type>(extended): <short summary>`

### Allowed Types
- **feat**: A new feature (e.g., `feat(extended): support configurable clip duration 2s/3s/5s`)
- **fix**: A bug fix for an extended module
- **docs**: Documentation updates under `plan/` or `extended/`
- **style**: Code formatting in extended modules

### Example Commit Messages
```bash
git commit -m "feat(extended): add video clip duration parameter to CLI and API"
git commit -m "docs(extended): update system architecture for Dell T7920 Ollama pipeline"
```
