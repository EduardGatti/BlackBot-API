# 🤖 Black Bot

Um bot avançado para Discord com **sistema de tickets, auditoria, CAPTCHA, moderação e muito mais**!

## 📌 Funcionalidades
- 🎫 **Sistema de Tickets**
- 🔒 **Sistema de Auditoria** (Registra exclusões, edições, bans, etc.)
- 🔍 **CAPTCHA para novos membros**
- 🚨 **Proteção contra links suspeitos**
- 🔨 **Moderação (ban, kick, mute)**
- 🗑️ **Comando `!clear` para apagar mensagens**
- 🎉 **Boas-vindas automáticas**

---

## 🛠 **Comandos**
### **🎫 Tickets**
| Comando | Descrição |
|---------|-----------|
| `!ticket` | Envia um painel para criar tickets |

### **🚨 Moderação**
| Comando | Descrição |
|---------|-----------|
| `!ban @usuário [motivo]` | Bane um usuário |
| `!kick @usuário [motivo]` | Expulsa um usuário |
| `!unban ID` | Remove um ban |
| `!clear <quantidade>` | Apaga mensagens |

### **🔒 Sistema de Segurança**
- **Auditoria:** Todas as ações são registradas no canal `#logs`.
- **Proteção de Links:** Links suspeitos são detectados e o usuário é banido.
- **CAPTCHA:** Novos membros precisam resolver um código para entrar.

---

## ⚙️ **Configuração**
1. **Criar os canais**: `logs`, `verifycaptcha`, `welcome`.
2. **Definir cargos**: `admin`, `suport`, `assistant`, `verifyAccepted`.
3. **Rodar o bot:**
    `source .venv/bin/activate`
    `pip install -U discord.py`
    `pip install pillow`
---

## 🚀 **Como Contribuir**
1. Faça um **fork** do repositório.
2. Crie uma **branch** (`feature/nova-funcionalidade`).
3. Faça um **commit** (`git commit -m "Adicionei nova funcionalidade"`).
4. Envie um **Pull Request**!

---

Agora, o bot está **pronto para ser commitado no GitHub**. 🚀  
Se precisar de mais alguma coisa, só avisar! 😃

