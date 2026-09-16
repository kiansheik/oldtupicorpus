# Estruturas temporais com îekyî e îub

Expressões avaliadas no namespace de `araujo_catecismo_1686:0016`.

```python
# 1. Hipótese ativa atual do léxico Pydicate
îekyî * +oré
# => oroîekyî

# 2. Verbo posicional independente
îub * +oré
# => oroîub

# 3. Verbo posicional subordinado no gerúndio
(îekyî * +oré) << (îub * +oré)
# => oroîekyî oroîupa

# 4. Temporal simples
eme * (îekyî * ixé)
# => xe îekyîeme

# 5. Temporal complexo: a oração matriz é necessária para o renderizador
(+endé * tupãmongetá).imp() << (
    irã + ((îub * oré) >> (îekyî * oré)) << béno
)
# => etupãmongetá irã oré îekyî oré rúme béno

# 6. Paralelo de Anchieta com erekó
(poî * ixé) << (erekó * ixé)
# => xepoî xererekóreme
```

Observações:

- O registro histórico aprovado usa a expressão completa em
  `historic/araujo_catecismo_1686.tu.py` e rende `oré îekyî oré rúme béno`
  dentro da oração matriz.
- O cadastro atual `îekyî = Verb("îekyî")` o trata como verbo ativo quando
  isolado. A classificação independente continua uma questão filológica; o
  match da oração completa não a resolve.
- O temporal citado no dicionário a partir de Anchieta, *Poemas* 102, aparece
  como `Xe îekyîme`; o Pydicate atualmente rende `xe îekyîeme`.
- Em `xepoî xererekóreme`, a anotação Pydicate marca as duas ocorrências de
  `xe` como `OBJECT:1ps`; o sujeito de terceira pessoa não está expresso. A
  árvore semântica genérica não distingue essa função e não deve ser usada
  sozinha para traduzir o exemplo.
- Os arquivos `*.pydicate.json` são gerados por
  `generate_pydicate_outputs.py` e contêm o prompt de tradução, a forma
  anotada, a representação semântica e a árvore Forest de cada objeto.
