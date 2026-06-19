# AppSec Kit

CLI interativo que configura ferramentas de segurança para esteiras CI/CD com um único comando. Roda no projeto do dev e gera os arquivos prontos para uso.

**Suporte:** Python · Node.js · GitHub Actions

---

## O que ele instala

| Camada | Python | Node.js |
|---|---|---|
| SAST | Bandit | Semgrep |
| Dependency scanning | pip-audit | npm audit |
| Secret scanning | Gitleaks + detect-secrets | Gitleaks + detect-secrets |
| Pre-commit hooks | pre-commit | pre-commit |

---

## Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) ou pip
- Git inicializado no projeto-alvo (`git init`)

---

## Instalação

### Via uv (recomendado)

```bash
uv tool install appsec-tool-kit
```

### Via pip

```bash
pip install appsec-tool-kit
```

### Direto do repositório (desenvolvimento)

```bash
git clone https://github.com/seu-usuario/appsec-tool-kit.git
cd appsec-tool-kit
uv sync
uv run appsec-kit
```

---

## Tutorial passo a passo

### Passo 1 — Acesse o diretório do seu projeto

```bash
cd /caminho/do/seu/projeto
```

> O kit detecta automaticamente o tipo de projeto pelo conteúdo do diretório.

---

### Passo 2 — Execute o wizard

```bash
appsec-kit
```

Você verá a tela inicial:

```
╭──────────────────────────────────────────────────────╮
│  AppSec Kit  –  Security toolkit for CI/CD pipelines │
╰──────────────────────────────────────────────────────╯

Detected: Python project

? Project type:
> Python
  Node.js
```

---

### Passo 3 — Confirme o tipo de projeto

O kit detecta automaticamente se é **Python** ou **Node.js** pelo conteúdo do diretório:

- Python → presença de `pyproject.toml`, `requirements.txt`, `setup.py` ou `Pipfile`
- Node.js → presença de `package.json`

Confirme ou altere com as setas e pressione `Enter`.

---

### Passo 4 — Confirme o diretório-alvo

```
? Target directory: [.]
```

Pressione `Enter` para usar o diretório atual ou informe outro caminho:

```
? Target directory: ../meu-outro-projeto
```

---

### Passo 5 — Selecione as camadas de segurança

```
? Security layers to configure:
 > [x] SAST (Static Analysis)
   [x] Dependency Scanning
   [x] Secret Scanning
   [x] Pre-commit Hooks
```

Use `Espaço` para marcar/desmarcar, `Enter` para confirmar.
Por padrão todas as camadas ficam selecionadas.

---

### Passo 6 — Aguarde a geração dos arquivos

```
  ✓  .github/workflows/security.yml  (created)
  ✓  .pre-commit-config.yaml         (created)
  ↻  pyproject.toml                  (updated)
```

---

### Passo 7 — Siga as instruções pós-instalação

O wizard exibe os próximos passos automaticamente:

```
╭─ Next steps ──────────────────────────────────────────╮
│  pip install pre-commit detect-secrets                 │
│  detect-secrets scan > .secrets.baseline               │
│  pre-commit install                                    │
│                                                        │
│  # Commit e push para ativar o GitHub Actions:        │
│  git add .github/ .pre-commit-config.yaml             │
│  git commit -m "chore: add appsec security config"    │
│  git push                                             │
╰───────────────────────────────────────────────────────╯
```

Execute esses comandos na ordem.

---

## O que é gerado

### `.github/workflows/security.yml`

Workflow do GitHub Actions com jobs separados por camada:

- **SAST** — análise estática roda a cada push/PR
- **Dependency scan** — verifica vulnerabilidades nas dependências
- **Secret scanning** — Gitleaks varre o histórico git em busca de segredos expostos

O workflow é acionado em push e pull requests para `main` e `master`.

---

### `.pre-commit-config.yaml`

Hooks que rodam localmente antes de cada commit:

**Python:**
```yaml
repos:
  - repo: https://github.com/PyCQA/bandit      # SAST
  - repo: https://github.com/Yelp/detect-secrets # secrets
  - repo: https://github.com/pypa/pip-audit      # dependências
```

**Node.js:**
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets # secrets
  - repo: https://github.com/gitleaks/gitleaks   # secrets
  - repo: local                                   # npm audit
```

---

### `pyproject.toml` (apenas Python)

Adiciona configuração do Bandit ao arquivo existente:

```toml
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = []
```

---

## Casos de uso comuns

### Só quero pre-commit, sem CI

Execute o wizard e desmarque as camadas SAST, Dependency Scanning e Secret Scanning. Mantenha apenas **Pre-commit Hooks** selecionado.

### Só quero o GitHub Actions, sem pre-commit

Desmarque **Pre-commit Hooks** e mantenha as outras camadas.

### Projeto já tem `.pre-commit-config.yaml`

O kit sobrescreve o arquivo com status `(updated)`. Faça backup antes se necessário:

```bash
cp .pre-commit-config.yaml .pre-commit-config.yaml.bak
appsec-kit
```

---

## Atualizando versões dos hooks

As versões dos hooks pre-commit ficam fixadas em `.pre-commit-config.yaml`. Para atualizar todas para o latest:

```bash
pre-commit autoupdate
```

---

## Ferramentas utilizadas

| Ferramenta | Finalidade | Docs |
|---|---|---|
| [Bandit](https://bandit.readthedocs.io/) | SAST para Python | bandit.readthedocs.io |
| [Semgrep](https://semgrep.dev/) | SAST para JavaScript/TypeScript | semgrep.dev |
| [pip-audit](https://pypi.org/project/pip-audit/) | CVEs em dependências Python | pypi.org/project/pip-audit |
| [detect-secrets](https://github.com/Yelp/detect-secrets) | Detecção de segredos | github.com/Yelp/detect-secrets |
| [Gitleaks](https://gitleaks.io/) | Varredura de segredos no histórico git | gitleaks.io |
| [pre-commit](https://pre-commit.com/) | Framework de git hooks | pre-commit.com |
