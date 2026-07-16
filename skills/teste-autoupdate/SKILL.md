---
name: teste-autoupdate
description: Skill-sonda para testar o auto-update do SkillHub. Use quando o usuário pedir para "testar auto-update", "checar a versão da skill", "qual versão da teste-autoupdate" ou invocar /teste-autoupdate.
---

# teste-autoupdate

Skill-sonda usada só para verificar se o auto-update está funcionando. Ela carrega um "carimbo" de versão fixo no texto; quando uma versão nova é publicada, o carimbo muda — então dá para saber, pela resposta, qual versão chegou na máquina.

## Quando usar
- O usuário pede para testar o auto-update ou saber qual versão da skill está instalada.

## O que responder
Responda exatamente com o bloco abaixo (sem alterar o carimbo):

```
✅ teste-autoupdate ATIVA
Carimbo de versão: v1 (publicada em 16/07/2026)
Se você está vendo "v1", esta é a versão inicial.
```
