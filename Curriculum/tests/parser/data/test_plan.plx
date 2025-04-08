<?xml version="1.0" encoding="utf-8"?>
<Документ xmlns="urn:schemas-microsoft-com:xml-diffgram-v1">
  <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <dsMMISDB xmlns="http://tempuri.org/dsMMISDB.xsd">
      <Планы Квалификация="Test Qualification" ГодНачалаПодготовки="2023" />
      <ПланыЦиклы Код="C1" Цикл="Test Cycle 1" Идентификатор="TC1"/>
      <ПланыЦиклы Код="C2" КодРодителя="C1" Цикл="Test Child Cycle 1.1" Идентификатор="TCC1.1"/>
      <ПланыСтроки Код="S1" КодБлока="C2" Дисциплина="Test Discipline 1" ТипОбъекта="2"/>
      <ПланыНовыеЧасы КодОбъекта="S1" КодВидаРаботы="101" КодТипаЧасов="1" Количество="10" Курс="1" Семестр="1"/>
      <СправочникВидыРабот Код="101" Название="Лекционные занятия"/>
      <СправочникТипаЧасов Код="1" Наименование="Часы в объемных показателях"/>
      <СправочникТипОбъекта Код="2" Название="Дисциплины"/>
    </dsMMISDB>
  </diffgr:diffgram>
</Документ>
