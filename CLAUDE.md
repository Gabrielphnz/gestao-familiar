# Gestão Financeira

Projeto da Aureate Sistemas. Repositorio: `Gabrielphnz/gest-ao-financeira` (privado).

## Versionamento — leia antes de mexer

Este projeto e versionado no GitHub. **Toda alteracao precisa virar commit e ser
enviada**, senao o que esta no ar deixa de corresponder ao que esta registrado.

Ao terminar um conjunto de mudancas:

```bash
git add -A
git commit -m "descricao do que mudou"
git push
```

Nao deixe alteracao sem commit ao encerrar a conversa. Se houver algo pendente,
avise o Gabriel explicitamente.

## Segredos

O `.gitignore` ja exclui `.env`, `service-account*.json`, chaves e afins.
**Nunca** remova essas linhas nem force o envio desses arquivos. Se precisar
documentar uma variavel, use `.env.example` com o valor em branco.

## Publicacao

Confira o `firebase.json` e o `.firebaserc` antes de qualquer `firebase deploy`:
varias pastas desta maquina apontam para projetos Firebase diferentes, e um
deploy na pasta errada tira um sistema de cliente do ar.
