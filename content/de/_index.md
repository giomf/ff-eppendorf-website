---
title: Freiwillige Feuerwehr Hamburg-Eppendorf
description: Technischer Zug - F1951
content_blocks:
- _bookshop_name: hero
  heading:
    title: Freiwillige Feuerwehr Eppendorf
    content: Technischer Zug - F1951
    align: start
  background:
    backdrop: /assets/img/hero.jpg
  illustration:
    image: /assets/img/logo.png
    width: 20
  orientation: horizontal
  #cover: true

- _bookshop_name: articles
  heading:
    title: Einsätze
    align: start
  input:
    section: einsaetze
    sort: date
    nested: true
  limit: 9
  hide-empty: true
  more:
    title: Weitere Einsätze
    link: einsaetze/page/2/
  class: border-0 card-zoom card-body-margin

- _bookshop_name: articles
  heading:
    title: Aktuelles
    align: start
  input:
    section: aktuelles
    sort: date
    nested: true
  limit: 9
  hide-empty: true
  more:
    title: Weiteres Aktuelles 
    link: aktuelles/page/2/
  class: border-0 card-zoom card-body-margin
---
