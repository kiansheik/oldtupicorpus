from historic.lexicon import load_lexicon

globals().update(load_lexicon())


bettendorff_compendio = [
    # Santa Cruz
    ((saba * (santa_cruz * aang)) * esé)
    + (endé * (pysyro.imp()) * oré)
    + ((tupan == (oré * îara.voc())))
    + ((sara * (-(oré * amotar))) * suí),
    (((tuba + tayra + espirito_santo) * era) * pupé),
    (amen + jesus),
    # Pai nosso
    (oré * tuba).voc() @ (((pe * ybaka)) + (sara * ikó).voc())
    + (amo * (pyra * moeté))
    + (ikó * (nde * era)).perm(),
    (ur * (nde * reino)).perm(),
    (monhang * (emi * (potar * nde)) * îe).perm()
    + (pe * yby)
    + (pe * ybaka)
    + (îabé * (monhang * ae * îe)),
    (((emi * (u * oré)) @ (nduara * (ara * iabiõ))) * (meeng * +endé).imp())
    + kori
    + (oré * supé),
    ((+nde * nhyron).imp() + (oré * angaipaba * esé) + (oré * supé))
    + (îabé * ((((sara * (erekomemûã * oré))) * supé) + (oré * nhyron))),
    (endé * -(mo * (ar / ukar)).imp() * oré) + (tentação * pupé),
    ((oré * ((pysyro * endé))).imp() << te) + ((mbae / aiba) * suí),
    (amen + jesus),
    # Ave Maria
    cop() * avemaria * (bae * ((esé * graça) + v(ynysema))),
    (amo * (nde * irun)) + (ikó * (îandé * îara)),
    (amo * (pyra * (mombeu / katu))) + (ikó * +endé) + (kunhã * suí),
    cop() * ((pyra * (mombeu / katu)) + abé) * (cop() * (nde * membyra) * jesus),
    (cop() * santamaria * (tupan * sy))
    + (+endé * tupãmongetá).imp()
    + (esé * (cop() * oré * (bae * v(angaipaba))))
    + koyr
    << (irã + ((îub * oré) >> (îekyî * oré)) << béno),
    (amen + jesus),
    # salva rainha
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
        >> ((jatf * (+endé * (epîak / ukar))).imp() + (oré * supé))
    ),
    cop()
    * (nheraneym.voc())
    * ((sara * v(poreaûsuberekó)).voc())
    * ((bae * v(een)).voc())
    * virgem_maria.voc(),  # fix absoluta m
    ((cop() * santamaria * (tupan * sy)) + (v(angaturama).perm() * +oré) << ne)
    + (esé * (pûera * (emi * (christo * enõî))))
    + (
        ri * (rama * (saba * (oré * îekosub)))
    ),  # îekosupagûama here is îekosuBagûama in bettendorf, displaying already some early divergences of loss of phonetic composition which we see in nheengatu
    (amen + jesus),
    # Creio em Deus Padre
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
    (esé * (ybyrá / îoasaba))
    + (amo * (pyra * moîar) + (ikó * +aebae))
    + (amo * (pyra * îuká))
    + (amo * (pyra * tym) + (ikó * +aebae)),
    (+jesus * gûeîyb + (pe * (yby * apytera))),
    (pupé * (ara * mosapyr.card()))
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
    +ixé * erobîar * espirito_santo,
    +ixé * erobîar * santa_igreja,
    +ixé
    * erobîar
    * (((santos * (ikó / katu)).base_nominal(True) * (mo * îaok) * îe).redup()),
]
