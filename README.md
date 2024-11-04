# Chat Bot avec une base de connaissances (KB)

## Introduction

Chat Bot personnel avec plusieurs outils:
- Google search
- Image server
- RAG

![bot-kb](images/bot-kb.png)

## Architecture

![architecture-kb](images/archi.png)


Utilisation de [LangChain](https://langchain.readthedocs.io/en/latest/index.html) pour fabriquer une base de données de connaissances en locale avec le contenu du fichier [devmtl-RAG.txt](data/devmtl-RAG.txt).

Utilisation de [OpenAI](https://platform.openai.com/docs/introduction) pour le [LLM](https://www.mlq.ai/what-is-a-large-language-model-llm/) (Large Language Model).

Gestion des routes sémantiques avec [semantic-router](https://github.com/aurelio-labs/semantic-router)

Utilisation d'un [Rerank](https://python.langchain.com/docs/integrations/retrievers/flashrank-reranker/) de résultats pour améliorer la pertinance des extraits de la base Vectorielle.

Utilisation de [SreamLit](https://docs.streamlit.io/) pour gérer le server et l'interface Web du Bot.

## Le serveur d'image ComfyUI

Pour générer des images, voici le lien pour configurer [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

Attention, le fichier [workflow.json](workflow.json) qui correspond à l'export d'un workflow API fonctionnel sur votre serveur ComfyUI 
doit être générer à partir de votre configuration, voir [Comment comment le faire ici](https://9elements.com/blog/hosting-a-comfyui-workflow-via-api/)

Il est necessaire d'avoir un serveur ComfyUI dont l'URL est configuré dans le fichier [.env](.env)
```sh
COMFYUI_SERVER_ADDRESS=
```

## La configuration de l'outil GoogleSearch

Pour utiliser le tool GoogleSearch dans langchain, il faut configurer [Google Search](https://python.langchain.com/docs/integrations/tools/google_search/)


Pour utiliser GoogleSearch, il est necessaire d'avoir ceci configuré dans le fichier [.env](.env)
```sh
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
```

## La configuration de Python

Pour installer les librairie Python requises:

```sh
./setup.sh
```

## La configuration de Langsmith

Tous les appels à langchain sont loggés sur Langsmith.
Vous devez vous inscrire et générer un token en suivant [cette procedure](https://www.langchain.com/langsmith)

```sh
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="TOKEN"
LANGCHAIN_PROJECT="your-project"
```

## La configuration du LLM

J'utilise [OpenAI](https://platform.openai.com/docs/overview) [gpt-4o-mini](https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/) comme LLM, vous devez avoir un compte chez OpenAI et configurer [le token d'API](https://platform.openai.com/docs/api-reference/authentication):

```sh
OPENAI_API_KEY=
```

## La configuration complète

Configuration complète du fichier .env (à créer)
```sh
COMFYUI_SERVER_ADDRESS=
OPENAI_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT="semantic-router"
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
```

Pour exécuter le chat Bot:
```sh
./start.sh
```

Vous pouvez maintenant poser votre question...
