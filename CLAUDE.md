# Gestão Financeira

Projeto da Aureate Sistemas. Repositório: `Gabrielphnz/gestao-familiar` (privado).

## Versionamento — leia antes de mexer

Este projeto é versionado no GitHub. **Toda alteração precisa virar commit e ser
enviada**, senão o que está no ar deixa de corresponder ao que está registrado.

Ao terminar um conjunto de mudanças:

```bash
git add -A
git commit -m "descrição do que mudou"
git push
```

Não deixe alteração sem commit ao encerrar a conversa. Se houver algo pendente,
avise o Gabriel explicitamente.

## Segredos

O `.gitignore` já exclui `.env`, `service-account*.json`, chaves e afins.
**Nunca** remova essas linhas nem force o envio desses arquivos. Se precisar
documentar uma variável, use `.env.example` com o valor em branco.

## Publicação

Confira o `firebase.json` e o `.firebaserc` antes de qualquer `firebase deploy`:
várias pastas desta máquina apontam para projetos Firebase diferentes, e um
deploy na pasta errada tira um sistema de cliente do ar.
