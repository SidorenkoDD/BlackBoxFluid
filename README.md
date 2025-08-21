Fluid compositional modeling with use of EOS

# Python PVT сompositional modeling  #

Модуль для композиционного моделирования PVT-свойств флюида


## Описание ##

Данный модуль является результатом изучения композиционного моделирования флюида, активно дополняется и развивается. 

Автор старается избегать ошибок в расчетных модулях, но не гарантирует их отсутствия.

## Реализованный функционал ##

* Создание состава до С45
* Проведение анализа стабильности двухфазного равновесия при заданных РТ условиях
* Проведение flash-расчета при заданных РТ условиях
* Построение фазовой диаграммы


## Реализованные расчетные модули ##

### УРС ###
* Peng-Robinson Peneloux
* SRK
* *Brusilovsky EOS -  в работе*


### Корреляции свойств С6+ компонент ###

#### P critical ####
* Kesler - Lee
* Rizari - Daubert
* Pedersen
* Standing

#### T critical ####
* Roess
* Nokey
* Cavett
* Kesler-Lee
* Pedersen
* Standing

#### Critical volume ####
* Rizari - Daubert
* Hall - Yarborough

#### Acentric factor ####
* Edmister
* Rizari - Al-Sahhaf

#### Shift Parametr ####
* Jhaveri-Youngren

#### BIPS ####
* Chueh-Prausnitz
* Zero






