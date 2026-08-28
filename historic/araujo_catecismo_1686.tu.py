from historic.lexicon import load_lexicon

globals().update(load_lexicon())
third_day = ara * mosapyr.card()
# call it l for writting convenience
l = [
    # @page 1
    # @section Livro I. Dos primeiros elementos da Fé Christãa, Summa dos mysterios, & doutrina Christãa
    # @subsection Oração do sinal do Cruz
    ((saba * (santa_cruz * aang)) * esé)
    + (endé * (pysyro.imp()) * oré)
    + ((tupan == (oré * îara.voc())))
    + ((sara * (-(oré * amotar))) * suí),
    (((tuba + tayra + espirito_santo) * era) * pupé),
    (amen),
    # @subsection Padre Noßo
    (oré * tuba).voc() @ (((pe * ybaka)) + (sara * ikó).voc())
    + (amo * (pyra * moeté))
    + ((nde * era) * ikó).perm(),
    (ur * (nde * reino)).perm(),
    # @pages 1-2
    (monhang * (emi * (potar * nde)) * îe).perm()
    + (pe * yby)
    + (pe * ybaka)
    + (îabé * (monhang * ae * îe)),
    # @line 1-2
    (((emi * (u * oré)) @ (nduara * (ara * iabiõ))) * (meeng * +endé).imp())
    + kori
    + orébe,
    #####
    ((+nde * nhyron).imp() + (oré * angaipaba * esé) + orébe)
    + (îabé * ((((sara * (erekomemûã * oré))) * supé) + (oré * nhyron))),
    (endé * -(mo * (ar / ukar)).imp() * oré) + (tentação * pupé),
    ((oré * ((pysyro * endé))).imp() << te) + ((mbae / aiba) * suí),
    (amen),
    # @subsection Ave Maria
    cop() * avemaria * (bae * ((esé * graça) + v(ynysema))),
    (amo * (nde * irun)) + (ikó * (îandé * îara)),
    (amo * (pyra * (mombeu / katu))) + (ikó * +endé) + (kunhã * suí),
    cop() * ((pyra * (mombeu / katu)) + abé) * (cop() * (nde * membyra) * jesus),
    (cop() * santamaria * (tupan * sy))
    + (+endé * tupãmongetá).imp()
    + (esé * (cop() * oré * (bae * v(angaipaba))))
    + koyr
    << (irã + ((îub * oré) >> (îekyî * oré)) << béno),
    (amen),
    # @subsection Salve Rainha
    (cop() * (salve_rainha == (poraûsubara * sy)) + ikobé.base_nominal(True))
    + (bae * v(een))
    + (saba * (oré * erobîar * îe))
    + (salve),
    (nde * supé)
    + (+oré * sapukai.redup()).circ(False)
    + (amo * (pyra * pea))
    + (amo * (eva * membyra)),
    (nde * supé) + ((+oré * nheangerur.circ(False)) << (oré * v(poasema)))
    << ((+oré * îaseo) + (pupé * ((ikód * ybytygûaîa) == (saba * îaseo)))),
    enein + (sara * ((esé * oré) + (îeruré))).voc(),
    ((eboûing * (nde * (esá / poraûsubara))) * (+endé * erobak.imp())) + (oré * koty),
    (aec)
    + (
        (iré * (syk * (ikód * (pûera * (saba * (pea * îe))))))
        >> ((jatf * (+endé * (epîak / ukar))).imp() + orébe)
    ),
    # @pages 2-3
    cop()
    * (nheraneym.voc())
    * ((sara * v(poreaûsuberekó)).voc())
    * ((bae * v(een)).voc())
    * virgem_maria.voc(),  # fix absoluta m
    ((cop() * santamaria * (tupan * sy)) + (v(angaturama).perm() * +oré) << ne)
    + (esé * (pûera * (emi * (christo * enõî))))
    + (
        ri * (rama * (saba * (oré * îekosub)))
    ),  # îekosubagûama here is îekosuBagûama in bettendorf, displaying already some early divergences of loss of phonetic composition which we see in nheengatu
    (amen),
    # @subsection Credo
    erobîar * +ixé * ((ttomtmetkbae) * (sara * (monhang * (abé + ybaka + yby)))),
    (
        +ixé
        * erobîar
        * ((cop() * (jesus / christo / abé)) * (tayra) * (oîepebae) * (asé * îara))
    ),  # fix abé rendering on correct element
    (
        pûera
        * (
            bae
            * (
                (pe * (saba * (espirito_santo * monhang * ae)))
                >> ((amo * pitangin) >> (((monhang) * îe)))
            )
        )
    ),
    (aebae * ar) + (suí * (cop() * (maria) * (ababykagûereyma))),
    (ponciopilato * ((amo * morubixaba) >> (ikó)))
    >> ((amo * (pyra * (erekó / memûã))) + (+aebae * ikó)),
    (esé * ybyraîoasaba)
    + (amo * (pyra * moîar) + (ikó * +aebae))
    + (amo * (pyra * îuká))
    + (amo * (pyra * tym) + (ikó * +aebae)),
    (+jesus * gûeîyb + (pe * (yby * apytera))),
    (pupé * third_day)
    + ((suí * (pûera * (bae * (manõ)))) + (+jesus * (ikobé / îebyr))),
    (upir * +jesus * îe) + (pe * ybaka),
    (koty * (ttomtmetkbae * ekatûaba)) + (+jesus * inv),
    aesuí + (+jesus * îur)
    << (
        (
            (((bae * (ikobé))) + ((pûera * (bae * (manõ)))) + paben)
            * (+jesus * (ekomonhang))
        )
    )
    + ne,
    (arobiar * espirito_santo),
    arobiar * santa_igreja,
    arobiar * (((santos * (ikó / katu)).base_nominal(True) * (mo * îaok) * îe).redup()),
    (arobiar * ((ekoangaîpaba * esé) + (moro * supé) + (tupan * nhyron))),
]


l += arobiar * (rama * (saba * (asé * (ikobé / îebyr))))
l += ((+(ixé)) * (erobîar)) * (((ikobé) @ (opbrmym)))
l += amen
# @subsection Artigos da Fé
# @page 4
l += catorse * (rama * (asé * (emi * erobîar)))
l += ((sete * ((nduara * (tupan * esé))))) + ((nã) + (+ae * ei))
l += arobiar * ((oîepé * (tupan)) @ (otmrme))
l += credo(tuba)
l += credo(tayra)
l += credo(espirito_santo)
l += credo(sara * opakatumonhanga)
l += credo(sara.var(1) * (moro * pysyro))
l += credo(
    sara * (meeng * (ikobé @ opbrmym))
)  # TODO: reconcile the bad r-ekobé grammar in the original, perhaps implement footnotes per line which can be added to the full version mentioning that in other versions it is tekobé and someone probably messed up so we corrected here as it is not linguistically significant that they most likely made a typo

l += (sete * (nduara * ((pûera * (saba * (jesusxto * îar * (asé * carne)))) * esé))) + (
    (nã) + (+ae * ei)
)

l += (arobiar << (aé)) * (
    (
        (
            (
                ((tupan @ tayra) + (pe * (saba * (espirito_santo * monhang * +ae))))
                + ((amo * pitanga) + (pûera * (saba * (+ae * monhang * (îe)))))
            )
        )
    )
)


l += (
    arobiar
    * (
        ((virgem_maria * suí) + (saguera(ae * ar)))
        + (((amo * ababykagûereyma) + (ikó * +ae)).base_nominal() * pupé)
    )
) + memen

l += arobiar * (
    (asé * esé)
    + (
        ybyraîoasaba * esé
        + (pyreramo(moîar) + (pyreramo(îuká) + (pyreramo(tym) + (+ae * ikó))))
    )
)


l += arobiar * (
    (
        (abé.var(1) * ((pe * (yby * apytera)) + saguera(+ae * gûeîyb)))
        * (
            saguera(
                (
                    (
                        (
                            (asé * (tuba / ypyOrigin))
                            @ ((karaiba / etá) * (pûera * soul))
                        )
                        @ (
                            bae
                            * (
                                (
                                    rama
                                    * ((((((aepe >> (+tupan * îur)))).base_nominal())))
                                    * arõ
                                )
                            )
                        )
                    )
                    * (enosem)
                )
            )
        )
    )
)
# @page 5
l += arobiar * ((esé * third_day) + (saguera(((+jesus * (ikobé / îebyr))))))
l += arobiar * ((abé.var(1) * risetoheaven) * rightsidegod)
l += arobiar * ((abé.var(1) * bondadenomundo * (pûera * n(ae * sinfullife))) * payment)
# @subsection Mandamentos da Ley de Deos
l += dez * (saba * (asé * (tupan * ekomonhang)))
l += (eimoeté * (oîepé * tupan)).imp()

l += (anheté + (+nde * (-ei / tenhen)) << (nde * enõî * (tupan * era))).imp()
marãtekó.definition = "state of work, job, working"
l += eimoeté * (domingo_e_feriado)

l += eimoeté * pais
l += -(+nde * apiti * moro).imp()
l += -(+nde * potar * moro).imp()
mondarõ = Verb("mondarõ")
l += -(+nde * mondarõ).imp()
moem = Noun("emo'em", "(t)")
l += -(+nde * v(moem)).imp() + (esé * abá)
momotar = Verb("momotar")
apixara = Noun("apixara", "(t)")
emirekó = Noun("emirekó", "(t)")
l += -(+nde * momotar * îe).imp() + esé * ((nde * apixara) * emirekó)
l += nã + ((bae * ei) * pupé) + (paben + (aîpo * îub))
opkmbt = opakatu + (mbae + tetiruã)
l += (
    opkmbt
    + (((asé * aûsub * +opkmbt).base_nominal()) * sosé)
    + (asé * (tupan * aûsub.base_nominal()))
)
l += (îabé * (+asé * aûsub * îe)) + (asé * aûsub * (og * apixara))
# @page 6
# @subsection Mandamentos da Santa Madre Igreja
sinco = Number("sinco", "five")
smi = Noun("Santa Madre Igreja")
l += sinco * (saba * (asé * (smi * ekomonhang)))
esebé = Postposition(
    "esebé", definition="(t) (posp.) - com, juntamente com, assim como"
)
missa = ProperNoun("missa", definition="mass")
endub = Verb("endub")
l += (esé * domingo) + ((esebé * noworkday)) + (missa * endub).base_nominal()
seîxu = Noun("seîxu", "ano")
l += (iabiõ * seîxu) + (îe * mombeu).var(1).base_nominal()

araujo_catecismo_1686 = l
if __name__ == "__main__":
    for expr in araujo_catecismo_1686:
        print(expr.eval())
