# Simulador de um sistema de escaneamento de feixe sobre um tumor sólido para pacientes posicionados na vertical
---

## Índice de Problemas Comuns

1. [Falha ao Abrir Dispositivo HID](#1-falha-ao-abrir-dispositivo-hid)
2. [Espelho Não Se Movimenta](#2-espelho-não-se-movimenta)
3. [Permissão Negada em Dispositivo](#3-permissão-negada-em-dispositivo)

---

### 1. Falha ao Abrir Dispositivo HID
**Erro:** 
```
File "hid.pyx", line 143, in hid.device.open OSError: open failed
```

**Solução:** 
- Execute o programa utilizando o comando `sudo` para obter privilégios elevados.
- Certifique-se de utilizar a versão correta do Python, especificando o ambiente Python apropriado.

---

### 2. Espelho Não Se Movimenta
**Erro:** 
- O espelho não responde ou não se move como esperado.

**Solução:** 
- Verifique se a conexão com a fonte de alimentação está correta.
- Confirme se a fonte de alimentação está configurada no modo `UPMODE:NORMAL`.

---

### 3. Permissão Negada em Dispositivo
**Erro:** 
```
Permission denied /dev/ttyusb0
```

**Solução:** 
- Altere as permissões do dispositivo utilizando o comando:
  ```
  sudo chmod 666 /dev/ttyusb0
  ```
  Isso permitirá o acesso ao dispositivo para todos os usuários.

---

