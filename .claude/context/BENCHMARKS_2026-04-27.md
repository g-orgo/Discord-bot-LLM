# Benchmarks de Modelos Ollama e Fine-Tuning (2026-04-27)

## Escopo
- Projeto: raptor-chatbot-llm
- Objetivo 1: escolher o melhor modelo padrao para producao local com foco em latencia + qualidade.
- Objetivo 2: comparar opcoes de fine-tuning por modelo para o contexto do projeto.

## Benchmark 1 - Inferencia (latencia x precisao)

### Metodo
- 10 modelos locais avaliados via Ollama `/api/generate`.
- 6 testes objetivos: matematica, sequencia, classificacao, JSON estrito, dica MongoDB, resumo FastAPI.
- Para cada modelo:
  - warm-up inicial (nao contabilizado)
  - media de latencia por teste
  - score de precisao por aderencia a formato/resposta esperada
- Score final: 70% precisao + 30% velocidade.

### Ranking
| Pos | Modelo | Precisao | Latencia media (s) | Score final |
|---|---|---:|---:|---:|
| 1 | qwen2.5:7b | 0.8824 | 2.5533 | 0.7494 |
| 2 | openchat:latest | 0.8640 | 2.4992 | 0.7381 |
| 3 | llama3.1:8b | 0.6875 | 2.6481 | 0.6103 |
| 4 | llama3.2:3b | 0.6691 | 2.5301 | 0.6008 |
| 5 | zephyr:latest | 0.6029 | 2.9710 | 0.5428 |
| 6 | mistral:latest | 0.4816 | 2.7739 | 0.4628 |
| 7 | llama2:latest | 0.4816 | 3.3898 | 0.4485 |
| 8 | dolphin-phi:latest | 0.2904 | 4.1565 | 0.3008 |
| 9 | phi:latest | 0.2022 | 4.5047 | 0.2338 |
| 10 | orca-mini:latest | 0.1434 | 2.7295 | 0.2272 |

### Explicacao por modelo (Benchmark 1)
- qwen2.5:7b: melhor equilibrio geral; manteve alta aderencia em tarefas estritas e latencia estavel.
- openchat:latest: qualidade muito proxima do lider e latencia boa, mas menor consistencia em respostas com restricao curta.
- llama3.1:8b: bom desempenho bruto, mas perdeu pontos em formato estrito (variacoes de pontuacao/resposta).
- llama3.2:3b: rapido, mas caiu em aderencia de instrucoes curtas e respostas estritas em alguns casos.
- zephyr:latest: acertou bem em parte dos testes, porem com maior verbosidade e instabilidade em tarefas de formato.
- mistral:latest: tende a explicar demais quando a tarefa pede saida minima, reduzindo score de precisao objetiva.
- llama2:latest: menor confiabilidade em tarefas objetivas e maior latencia media para este conjunto.
- dolphin-phi:latest: baixa aderencia a formato estrito e latencia alta para o perfil de uso do projeto.
- phi:latest: respostas inconsistentes em tarefas objetivas e variacao de tempo elevada.
- orca-mini:latest: latencia razoavel, mas baixa taxa de conformidade aos formatos exigidos.

### Decisao do Benchmark 1
- Modelo escolhido como padrao do sistema: qwen2.5:7b
- Motivo: melhor score final no equilibrio entre rapidez e qualidade para o fluxo real do projeto.

---

## Benchmark 2 - Opcoes de fine-tuning por modelo

### Metodo
- Benchmark de viabilidade tecnica (estimativa) por modelo usando:
  - acuracia/latencia base do Benchmark 1
  - escala do modelo (estimativa em B)
  - custo de treino (horas estimadas)
  - VRAM estimada
  - ganho esperado de qualidade por estrategia
- Estrategias comparadas:
  - QLoRA_4bit (baixo custo, melhor ROI local)
  - LoRA_plus_DPO (alinhamento mais forte, custo medio)
  - Full_FineTune (maior teto de qualidade, custo alto)

### Ranking (melhor opcao por modelo)
| Pos | Modelo | Melhor opcao | Score fine-tuning |
|---|---|---|---:|
| 1 | qwen2.5:7b | QLoRA_4bit | 0.8658 |
| 2 | openchat:latest | QLoRA_4bit | 0.8588 |
| 3 | llama3.2:3b | Full_FineTune | 0.7999 |
| 4 | llama3.1:8b | QLoRA_4bit | 0.7777 |
| 5 | zephyr:latest | QLoRA_4bit | 0.7305 |
| 6 | mistral:latest | QLoRA_4bit | 0.6802 |
| 7 | llama2:latest | QLoRA_4bit | 0.6678 |
| 8 | dolphin-phi:latest | Full_FineTune | 0.5980 |
| 9 | orca-mini:latest | Full_FineTune | 0.5586 |
| 10 | phi:latest | Full_FineTune | 0.5536 |

### Explicacao por modelo (Benchmark 2)
- qwen2.5:7b: melhor candidato para QLoRA no projeto; alta base de qualidade com custo de treino moderado.
- openchat:latest: tambem forte em QLoRA, mas levemente abaixo do qwen2.5:7b no score combinado.
- llama3.2:3b: por ser menor, full fine-tune fica mais viavel e pode recuperar qualidade com custo ainda administravel.
- llama3.1:8b: QLoRA e o caminho mais seguro para manter custo baixo sem sacrificar qualidade.
- zephyr:latest: QLoRA traz ganho com custo previsivel, mas parte de baseline inferior aos lideres.
- mistral:latest: tende a melhorar com QLoRA, porem baseline atual limita o teto para este caso.
- llama2:latest: custo/beneficio de tuning e aceitavel, mas base antiga reduz retorno comparado aos modelos mais novos.
- dolphin-phi:latest: exigiria tuning mais agressivo para competir; full fine-tune aparece melhor na estimativa.
- orca-mini:latest: somente tuning pesado melhora de forma perceptivel, ainda com limite de qualidade final.
- phi:latest: precisa de ajuste profundo para reduzir inconsistencias; full fine-tune supera adaptacoes leves.

### Recomendacao pratica para o projeto
- Curto prazo: manter qwen2.5:7b como padrao e iniciar QLoRA_4bit nele.
- Alternativa secundaria: openchat:latest com QLoRA_4bit se o comportamento do qwen fugir do estilo desejado.
- Evitar iniciar por modelos de baixo baseline (phi/orca/dolphin-phi), pois exigem tuning mais caro para chegar no mesmo nivel.

## Arquivos de saida gerados
- benchmark_ollama_models.py
- benchmark_ollama_models.json
- benchmark_finetuning_options.py
- benchmark_finetuning_options.json
