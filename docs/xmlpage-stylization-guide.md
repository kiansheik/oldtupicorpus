# Guia de estilização do PAGE XML

Este guia é a referência para a sintaxe leve, os atalhos e os açúcares de
edição aceitos por `scripts/xmlpage_to_html.py`.

Sempre que uma nova sintaxe ou substituição for adicionada ao conversor, atualize
este documento no mesmo patch que altera o código e os testes. O comando
`--help` lê este arquivo, então a ajuda do terminal acompanha este guia.

## Sintaxe do usuário

Use estas marcas diretamente no texto reconhecido/exportado da página.

### Atalhos de caracteres

- Sintaxe: `$`
  - Exemplo digitado: `coelum, $olem`
  - Como aparece no HTML: `coelum, ſolem`
  - Uso: transcrever o s longo.
- Sintaxe: `-p-`
  - Exemplo digitado: `a-p-aba -p-`
  - Como aparece no HTML: `aꝑaba ꝑ`
  - Uso: escrever o glifo abreviado `ꝑ`.
- Sintaxe: `a=e`, `o=e`
  - Exemplo digitado: `a=e o=e A=e O=e`
  - Como aparece no HTML: `æ œ Æ Œ`
  - Uso: escrever rapidamente as ligaduras latinas `æ` e `œ` sem trocar todo
    `ae` ou `oe` automaticamente. O sinal `=` evita colisões com trechos reais
    como `a-e` ou `o-e`.
- Sintaxe: `&`
  - Exemplo digitado: `R. & aba`
  - Como aparece no HTML: `R. & aba`
  - Uso: caractere literal. Não vira `R.` e não vira marca de parágrafo.

### Diacríticos antes da letra

- Sintaxe: `˜q`
  - Como aparece no HTML: `q̃`
- Sintaxe: `^y` ou `ˆu`
  - Como aparece no HTML: `ŷ` ou `û`
- Sintaxe: `´a`, acento grave + `e`, `¨i`, `¸c`
  - Como aparece no HTML: `á`, `è`, `ï`, `ç`
- Outros sinais aceitos antes de uma letra: `˙`, `˚`, `ˇ`, `˘`, `¯`
- Se o próximo caractere não for uma letra, o sinal fica literal.

### Formatação em linha

- Sintaxe: `**texto**`
  - Como aparece no HTML: texto em negrito.
- Sintaxe: `*texto*`
  - Como aparece no HTML: texto em itálico.
- Sintaxe: `__texto__`
  - Como aparece no HTML: texto sublinhado.
- Sintaxe: `~texto~`
  - Como aparece no HTML: texto riscado horizontalmente.
- Sintaxe: `|texto|`
  - Exemplo digitado: `ocäu|m|baeráma? oporomonhang|m|bae-`
  - Como aparece no HTML: as letras `m` recebem um risco vertical de manuscrito.
- Sintaxe: `++texto++`
  - Como aparece no HTML: texto sobrescrito.
- Sintaxe: `--texto--`
  - Como aparece no HTML: texto subscrito.
- Sintaxe: `%40 texto%`
  - Exemplo digitado: `Tertio %40 $raecepto% [leitura provável]`
  - Como aparece no HTML: `Tertio` seguido de `ſraecepto` com 40% de opacidade
    visível, mais a nota `leitura provável` abaixo da página.
  - Uso: transcrever texto apagado ou muito claro quando a leitura é provável,
    preservando a palavra pesquisável no HTML. O número deve ser de 0 a 100 e
    representa a porcentagem de opacidade visível estimada pelo transcritor.

As marcas de formatação não entram no cálculo visível de largura da linha, mas
o texto marcado continua aparecendo.

### Notas

- Sintaxe: `[texto da nota]`
  - Como aparece no HTML: uma referência numerada na linha e uma nota abaixo da
    caixa da página.
- Sintaxe: `[]`
  - Como aparece no HTML: os colchetes vazios ficam no texto.
- Sintaxe: `\[texto literal\]`
  - Como aparece no HTML: `[texto literal]`
  - Uso: quando os colchetes fazem parte do texto e não devem virar nota.
- Sintaxe dentro de nota: `[ver \[sic\]]`
  - Como aparece na nota: `ver [sic]`
- Colchetes sem fechamento ficam no texto.
- Colchetes internos ficam dentro da mesma nota: `[g[eral]]` vira uma nota com
  texto `g[eral]`.

### Marca de resposta

- Sintaxe: `R.`
  - Como aparece no HTML: `R.` continua sendo texto, mas recebe uma estilização
    parecida com a marca manuscrita.
- `R.` não vira `¶`.
- `&` não produz marca de resposta.

## Manutenção

- Atualize este guia sempre que adicionar sintaxe, atalho ou açúcar visual.
- Atualize `tests/xmlpage_to_html_test.py` no mesmo patch.
- Verifique se a nova marca afeta o texto pesquisável ou o cálculo de largura
  da linha.
- Prefira sintaxe explícita a substituições automáticas amplas.

## Uso do conversor

No Transkribus, abra a página do manuscrito e escolha `Export` no menu para
obter a representação XML/PAGE XML da página. Escolha `PageXML 2013` na
exportação; o conversor espera o namespace PAGE XML 2013. Não escolha
`PageXML 2019`. Esse XML é a entrada usada pelo conversor para gerar o HTML do
livro.

Depois de exportar o XML, rode:

```bash
python3 scripts/xmlpage_to_html.py input.xml
```

O conversor também aceita uma pasta de exportação do Transkribus. Nessa forma,
ele procura os documentos com `mets.xml`, lê a ordem das páginas no grupo
`PAGEXML`, confere se todos os arquivos declarados existem e gera um único HTML
contínuo com todas as páginas:

```bash
python3 scripts/xmlpage_to_html.py export_job_26821620
```

Para escolher o arquivo de saída:

```bash
python3 scripts/xmlpage_to_html.py --output livro.html export_job_26821620
```

Sem `--output`, o conversor escreve `output.html` no diretório atual.

Para imprimir este guia no terminal:

```bash
python3 scripts/xmlpage_to_html.py --help
```
