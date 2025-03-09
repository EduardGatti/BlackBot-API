# 🤖 **Black Bot**  

Um bot avançado para Discord com **sistema de tickets, auditoria, CAPTCHA, moderação e muito mais**!  

---

## 📌 **Funcionalidades Principais**  
✅ **🎫 Sistema de Tickets** – Gerencie suporte de forma eficiente.  
✅ **🔒 Auditoria Completa** – Registra exclusões, edições, bans e muito mais.  
✅ **🔍 CAPTCHA de Segurança** – Verificação para impedir bots.  
✅ **🚨 Proteção contra Links Suspeitos** – Bloqueia e bane automaticamente.  
✅ **🔨 Moderação Avançada** – Comandos de ban, mute e kick.  
✅ **🗑️ Limpeza de Mensagens** – Comando `!clear` para apagar mensagens.  
✅ **🎉 Boas-Vindas Automáticas** – Mensagem personalizada ao entrar.  

---

## 🛠 **Comandos Disponíveis**  
### 🎫 **Sistema de Tickets**  
| Comando | Descrição |  
|---------|-----------|  
| `!painel-ticket` | Envia um painel para abrir tickets |

### 🚨 **Moderação**  
| Comando | Descrição |  
|---------|-----------|  
| `!ban @usuário [motivo]` | Bane um usuário do servidor |  
| `!kick @usuário [motivo]` | Expulsa um usuário |  
| `!unban ID` | Remove o banimento de um usuário |  
| `!mute @usuário [tempo]` | Silencia temporariamente um usuário |  
| `!warn @usuário [motivo]` | Emite um aviso para o usuário |  
| `!clear <quantidade>` | Apaga um número específico de mensagens |

### 🔒 **Segurança & Auditoria**  
✔ **Auditoria** – Todas as ações são registradas no canal `#logs`.  
✔ **Proteção de Links** – Links suspeitos resultam em **ban automático**.  
✔ **Sistema de CAPTCHA** – Proteção contra bots e raids.  

---

## ⚙️ **Configuração Inicial**  
### 1️⃣ **Criar os canais necessários**  
- `📜│logs` – Registro de auditoria.  
- `🚨│alertas` – Alertas de bans, kicks e mutações.  
- `✅│verifycaptcha` – Canal para CAPTCHA de novos membros.  
- `🎉│welcome` – Mensagem automática de boas-vindas.  

### 2️⃣ **Criar os cargos necessários**  
- `admin` – Administradores com controle total.  
- `suport` – Suporte ao sistema de tickets.  
- `assistant` – Moderadores auxiliares.  
- `verifyAccepted` – Usuários que passaram pelo CAPTCHA.  
- `Mutado` – Usuários silenciados.  

---

## 🔧 **Como Rodar o Bot**  
### 1️⃣ **Instale as dependências**  
Certifique-se de que tem **Python 3.8+** instalado e execute:  
```bash
pip install -U discord.py pillow aiohttp
```
## 2️⃣ **Configure o bot**
- Edite ``main.py`` e adicione seu Token do Bot.
- Ajuste os IDs dos canais e cargos no código.

## 3️⃣ **Inicie o bot**
No terminal, execute:
```bash
python main.py
```
Caso queira rodar em segundo plano (Linux):
```bash
nohup python3 main.py &
```
---

## ⚙️ **Configuração**
### 🔧 **Passo a passo para rodar o bot**
1. **Instale os requisitos**  
   Certifique-se de ter o Python instalado e execute:  
   
bash
   pip install -U discord.py pillow aiohttp

---

## 🚀 **Como Contribuir**
1. Faça um **fork** do repositório.
2. Crie uma **branch** (`feature/nova-funcionalidade`).
3. Faça um **commit** (`git commit -m "Adicionei nova funcionalidade"`).
4. Envie um **Pull Request**!
5. 💡 Sugestões? Abra uma ``issue`` e compartilhe sua ideia!

---

## 📝 Licença
Este projeto é open-source. Sinta-se livre para usar, modificar e contribuir!
🔗 [GitHub: Black Bot Repository](https://github.com/EduardGatti/BlackBot-API)

---



