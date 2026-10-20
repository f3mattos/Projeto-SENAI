---
titulo: Procedimento para indisponibilidade de sistemas críticos
categoria: infraestrutura
versao: 3.0
vigente_desde: 2026-01-15
publico: interno
---

## Objetivo
Padronizar a resposta operacional imediata diante de quedas, interrupções totais ou degradação grave dos sistemas de produção da empresa.

## Pré-requisitos
- Confirmação de indisponibilidade geral afetando múltiplos usuários ou processos centrais de faturamento/vendas.

## Procedimento
1. Diante de relatos de que o portal de vendas, autenticação corporativa ou banco de dados de produção está fora do ar, o suporte deve imediatamente:
   - Consultar o painel de status em `https://status.empresa.local` para verificar se há incidente já registrado.
   - Testar a conectividade a partir de uma rede externa limpa.
2. Confirmada a queda, o incidente deve ser classificado compulsoriamente como **urgência alta**.
3. O operador deve propor e abrir imediatamente um chamado de severidade 1 (P1) com o título "INDISPONIBILIDADE: [Nome do Sistema]" contendo data, horário exato do início, mensagens de erro e escopo do impacto.
4. O chamado aciona a escala de plantão do time de Infraestrutura (SRE) via paging automático.
5. Uma mensagem de alerta deve ser publicada na página inicial corporativa informando a equipe interna sobre o trabalho em andamento e estimativa de retorno.

## Exceções
Manutenções programadas divulgadas com antecedência mínima de 48 horas não caracterizam incidente crítico imprevisto, exceto se ultrapassarem a janela autorizada em mais de 30 minutos.

## Responsável
Centro de Operações de Rede (NOC) e Engenharia de Confiabilidade (SRE).

## Data de revisão
Última revisão realizada em 05 de outubro de 2026.
