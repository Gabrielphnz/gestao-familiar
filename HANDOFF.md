# HANDOFF — Gestão Financeira

Vinculo Firebase desta pasta, verificado em 19/11/2026. **Confira este arquivo antes de
qualquer `firebase deploy`.** Ja houve deploy em projeto errado neste parque.

## Conta e projeto

| | |
|---|---|
| **Conta Google** | `gabrielphnz@gmail.com` |
| **Projeto Firebase** | `device-streaming-8cc2d083` |

## Destino do Hosting

| Site | Como e resolvido | Pasta publicada | URL | Hoje |
|---|---|---|---|---|
| `gestao-financeira-gp` | hosting.site | `public` | https://gestao-financeira-gp.web.app | **404** |

## Quem mais usa este projeto

- `Foodpark`

O projeto `device-streaming-8cc2d083` e compartilhado. **Nunca rode `firebase deploy` sem `--only`**:
um deploy amplo a partir desta pasta alcanca o que pertence as outras.

## Comando de deploy

```bash
firebase deploy --account gabrielphnz@gmail.com --project device-streaming-8cc2d083 --only hosting:gestao-financeira-gp
```

Passe sempre `--account` e `--project` explicitos. A conta ativa da CLI muda, e o
padrao silencioso e como um deploy vai parar no lugar errado.

## Atencao

O site `gestao-financeira-gp` **existe no projeto mas nunca recebeu deploy** — responde 404 hoje. A configuracao esta correta; o que falta e publicar.

## Se este arquivo estiver errado

Ele foi gerado a partir do `.firebaserc`, do `firebase.json` e de consulta as contas
na Firebase CLI. Se divergir da realidade, corrija **aqui tambem** — a pasta e a fonte
de verdade para quem pegar o projeto depois.
