# Prazos processuais cíveis — regras de contagem

## Regras gerais do CPC
- **Dias úteis**: só se contam dias úteis nos prazos processuais (art. 219). Prazos de direito
  material (prescrição, decadência, prazos contratuais) correm em dias corridos — CC art. 132.
- **Exclui o dia do começo e inclui o do vencimento** (art. 224). Prorroga-se para o primeiro dia
  útil se o início ou o vencimento cair em dia sem expediente, com expediente encerrado antes ou
  iniciado depois do normal, ou com indisponibilidade do sistema eletrônico (art. 224, §1º).
- **Recesso**: suspende-se o curso do prazo de 20 de dezembro a 20 de janeiro, inclusive (art. 220).
- **Diário eletrônico** (DJe / DJEN): considera-se publicação o **primeiro dia útil seguinte** ao da
  disponibilização (art. 224, §2º; Lei 11.419/2006, art. 4º, §3º), e o prazo começa no **primeiro
  dia útil seguinte** à publicação (art. 224, §3º).
- **Intimação pelo portal** (Lei 11.419/2006, art. 5º): considera-se feita no dia da consulta;
  se não houver consulta em **10 dias corridos** do envio, considera-se feita no fim desse prazo.
  O prazo começa no primeiro dia útil seguinte.
  ⚠️ Se houver intimação pelo DJEN e pelo portal sobre o mesmo ato, confira a regra adotada pelo
  tribunal e a jurisprudência atual do STJ — na dúvida, conte pela data mais antiga.
- **Citação** — termo inicial (art. 231): AR juntado aos autos (I); mandado juntado (II);
  ato do escrivão (III); fim da dilação do edital (IV); consulta eletrônica ou fim do prazo de
  consulta (V); **citação por meio eletrônico (e-mail): quinto dia útil seguinte à confirmação do
  recebimento** (IX, incluído pela Lei 14.195/2021).

## Prazo em dobro
- Fazenda Pública (art. 183), Ministério Público (art. 180), Defensoria Pública (art. 186) — e
  escritórios de prática jurídica de faculdades e entidades conveniadas (art. 186, §3º).
- Litisconsortes com procuradores diferentes, de escritórios distintos (art. 229) — **não se
  aplica a processo eletrônico** (art. 229, §2º).
- Não há dobro quando a lei fixar prazo próprio para o ente.

## Tabela (dias úteis, salvo indicação)
| Ato | Prazo | Fundamento |
|---|---|---|
| Contestação | 15 | art. 335 |
| Réplica | 15 | arts. 350 e 351 |
| Emenda da inicial | 15 | art. 321 |
| Manifestação genérica sem prazo fixado | 5 | art. 218, §3º |
| Apelação, agravo de instrumento, agravo interno, REsp, RE, e respectivas respostas | 15 | art. 1.003, §5º |
| Embargos de declaração | 5 | art. 1.023 |
| Pagamento voluntário no cumprimento de sentença | 15 | art. 523 |
| Impugnação ao cumprimento de sentença | 15 (após o prazo do art. 523) | art. 525 |
| Embargos à execução | 15 | art. 915 |
| Pagamento na execução de título extrajudicial | 3 | art. 829 |
| Juizado — recurso inominado | 10 | Lei 9.099/95, art. 42 |
| Juizado — embargos de declaração | 5 | Lei 9.099/95, art. 49 |

## Feriados que o script já considera
Nacionais fixos: 01/01, 21/04, 01/05, 07/09, 12/10, 02/11, 15/11, 20/11 (Lei 14.759/2023),
25/12. Móveis (forenses na prática da maioria dos tribunais): segunda e terça de Carnaval,
Sexta-feira Santa, Corpus Christi. Com `--justica-federal`: feriados da Lei 5.010/66, art. 62
(quarta a domingo da Semana Santa, 11/08, 01/11, 08/12; 20/12–06/01 já está no recesso).

## O que o script NÃO sabe (conferir sempre)
- Feriados estaduais e municipais da comarca e datas do tribunal (ex.: aniversário da cidade,
  data magna do estado, Quinta-feira Santa em alguns TJs, 08/12 em alguns estados).
- Portarias de suspensão de prazos e indisponibilidade do sistema (art. 224, §1º).
- Quarta-feira de Cinzas: em regra o expediente começa mais tarde — verifique a portaria;
  se houver expediente reduzido, o dia pode não contar como início/fim do prazo.

## Boas práticas
- Data-alvo interna = 2 dias úteis antes do vencimento.
- Registrar sempre: forma da intimação, data de disponibilização, data da publicação/ciência,
  termo inicial, prazo, dobro (sim/não), feriados considerados, vencimento.
