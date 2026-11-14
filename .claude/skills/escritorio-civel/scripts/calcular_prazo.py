#!/usr/bin/env python3
"""Cálculo de prazos processuais cíveis (CPC/2015) com memória de cálculo.

Considera: dias úteis (art. 219), exclusão do dia do começo e inclusão do vencimento (art. 224),
recesso de 20/12 a 20/01 (art. 220), feriados nacionais, Carnaval, Sexta-feira Santa,
Corpus Christi, regras de publicação no DJe/DJEN (art. 224, §§2º e 3º), intimação pelo portal
(Lei 11.419/2006, art. 5º) e citação eletrônica (art. 231, IX).

NÃO conhece feriados estaduais/municipais nem portarias de suspensão: informe-os com --feriados.

Exemplos:
  calcular_prazo.py --data 2026-03-02 --dias 15 --modo djen
  calcular_prazo.py --data 2026-03-02 --dias 15 --modo portal --consulta 2026-03-05
  calcular_prazo.py --data 2026-03-02 --dias 15 --modo citacao-eletronica
  calcular_prazo.py --data 2026-12-15 --dias 5 --modo simples --dobro --feriados 2026-12-08
  calcular_prazo.py --data 2026-03-02 --dias 30 --corridos      # prazo material (dias corridos)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta

DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def pascoa(ano: int) -> date:
    """Domingo de Páscoa (algoritmo de Meeus/Jones/Butcher, calendário gregoriano)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados_do_ano(ano: int, justica_federal: bool) -> dict[date, str]:
    p = pascoa(ano)
    f = {
        date(ano, 1, 1): "Confraternização Universal",
        date(ano, 4, 21): "Tiradentes",
        date(ano, 5, 1): "Dia do Trabalho",
        date(ano, 9, 7): "Independência",
        date(ano, 10, 12): "N. Sra. Aparecida",
        date(ano, 11, 2): "Finados",
        date(ano, 11, 15): "Proclamação da República",
        date(ano, 12, 25): "Natal",
        p - timedelta(days=48): "Carnaval (segunda)",
        p - timedelta(days=47): "Carnaval (terça)",
        p - timedelta(days=2): "Sexta-feira Santa",
        p + timedelta(days=60): "Corpus Christi",
    }
    if ano >= 2024:  # Lei 14.759/2023
        f[date(ano, 11, 20)] = "Consciência Negra"
    if justica_federal:  # Lei 5.010/66, art. 62
        f[p - timedelta(days=4)] = "Semana Santa (quarta) — JF"
        f[p - timedelta(days=3)] = "Semana Santa (quinta) — JF"
        f[date(ano, 8, 11)] = "Dia do Advogado / cursos jurídicos — JF"
        f[date(ano, 11, 1)] = "Todos os Santos — JF"
        f[date(ano, 12, 8)] = "N. Sra. da Conceição / Dia da Justiça — JF"
    return f


class Calendario:
    def __init__(self, extras: dict[date, str], justica_federal: bool):
        self.extras = extras
        self.jf = justica_federal
        self._cache: dict[int, dict[date, str]] = {}

    def feriado(self, d: date) -> str | None:
        if d in self.extras:
            return self.extras[d]
        if d.year not in self._cache:
            self._cache[d.year] = feriados_do_ano(d.year, self.jf)
        return self._cache[d.year].get(d)

    @staticmethod
    def recesso(d: date) -> bool:
        return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20)

    def motivo_nao_util(self, d: date, considerar_recesso: bool = True) -> str | None:
        if d.weekday() >= 5:
            return "fim de semana"
        f = self.feriado(d)
        if f:
            return f"feriado: {f}"
        if considerar_recesso and self.recesso(d):
            return "recesso (art. 220 CPC)"
        return None

    def util(self, d: date, considerar_recesso: bool = True) -> bool:
        return self.motivo_nao_util(d, considerar_recesso) is None

    def proximo_util(self, d: date, considerar_recesso: bool = True) -> date:
        d += timedelta(days=1)
        while not self.util(d, considerar_recesso):
            d += timedelta(days=1)
        return d

    def ajusta_para_util(self, d: date, considerar_recesso: bool = True) -> date:
        while not self.util(d, considerar_recesso):
            d += timedelta(days=1)
        return d


def fmt(d: date) -> str:
    return f"{d.strftime('%d/%m/%Y')} ({DIAS_SEMANA[d.weekday()]})"


def parse_data(s: str) -> date:
    s = s.strip()
    if "/" in s:
        dia, mes, ano = s.split("/")
        return date(int(ano), int(mes), int(dia))
    return date.fromisoformat(s)


def calcular(args) -> dict:
    extras = {}
    for item in filter(None, (args.feriados or "").split(",")):
        extras[parse_data(item)] = "informado pelo usuário (local/portaria)"
    cal = Calendario(extras, args.justica_federal)
    memoria: list[str] = []
    data = parse_data(args.data)
    dias = args.dias * (2 if args.dobro else 1)
    if args.dobro:
        memoria.append(f"Prazo em dobro: {args.dias} × 2 = {dias} dias.")

    # 1) Determinar o dia do começo (dia 0, excluído da contagem — art. 224)
    if args.corridos:
        marco = data
        memoria.append(f"Prazo em dias corridos (direito material). Data de referência: {fmt(marco)}.")
    elif args.modo == "djen":
        memoria.append(f"Disponibilização no DJe/DJEN: {fmt(data)}.")
        publicacao = cal.proximo_util(data)
        memoria.append(f"Publicação = 1º dia útil seguinte (art. 224, §2º): {fmt(publicacao)}.")
        marco = publicacao
        memoria.append("Contagem começa no 1º dia útil seguinte à publicação (art. 224, §3º).")
    elif args.modo == "portal":
        memoria.append(f"Envio da intimação ao portal: {fmt(data)}.")
        limite = data + timedelta(days=10)
        if args.consulta:
            ciencia = parse_data(args.consulta)
            if ciencia > limite:
                memoria.append(f"Consulta informada ({fmt(ciencia)}) é posterior ao 10º dia corrido; vale o limite.")
                ciencia = limite
            else:
                memoria.append(f"Consulta (ciência) em {fmt(ciencia)} (Lei 11.419/06, art. 5º, §1º).")
        else:
            ciencia = limite
            memoria.append(f"Sem consulta: intimação tácita no 10º dia corrido após o envio (art. 5º, §3º): {fmt(ciencia)}.")
        if not cal.util(ciencia):
            novo = cal.ajusta_para_util(ciencia)
            memoria.append(f"Ciência em dia não útil → considera-se no 1º dia útil seguinte (art. 5º, §2º): {fmt(novo)}.")
            ciencia = novo
        marco = ciencia
    elif args.modo == "citacao-eletronica":
        memoria.append(f"Confirmação do recebimento da citação eletrônica: {fmt(data)}.")
        marco = data
        for _ in range(5):
            marco = cal.proximo_util(marco)
        memoria.append(f"Dia do começo = 5º dia útil seguinte (art. 231, IX): {fmt(marco)}.")
    else:  # simples
        marco = data
        memoria.append(f"Dia do começo (intimação/juntada/ciência): {fmt(marco)} — excluído da contagem.")

    # 2) Contagem
    contados: list[tuple[int, date]] = []
    pulados: list[tuple[date, str]] = []
    if args.corridos:
        venc = marco + timedelta(days=dias)
        memoria.append(f"{dias} dias corridos a partir de {fmt(marco)} → {fmt(venc)}.")
        if not cal.util(venc, considerar_recesso=False):
            motivo = cal.motivo_nao_util(venc, considerar_recesso=False)
            novo = cal.ajusta_para_util(venc, considerar_recesso=False)
            memoria.append(f"Vencimento em dia sem expediente ({motivo}) → prorrogado para {fmt(novo)} (CC art. 132, §1º).")
            venc = novo
        inicio_contagem = marco + timedelta(days=1)
    else:
        d = marco
        n = 0
        inicio_contagem = None
        while n < dias:
            d += timedelta(days=1)
            motivo = cal.motivo_nao_util(d)
            if motivo:
                pulados.append((d, motivo))
                continue
            n += 1
            if inicio_contagem is None:
                inicio_contagem = d
            contados.append((n, d))
        venc = d
        memoria.append(f"1º dia da contagem: {fmt(inicio_contagem)}.")
        memoria.append(f"Contados {dias} dias úteis → vencimento em {fmt(venc)}.")

    alvo = venc
    if not args.corridos:
        k = 0
        while k < 2:
            alvo -= timedelta(days=1)
            if cal.util(alvo):
                k += 1
        if alvo <= marco:
            alvo = venc

    pulados_relevantes = [(d, m) for d, m in pulados if m != "fim de semana"]
    avisos = [
        "Conferir feriados estaduais/municipais e portarias de suspensão do tribunal no período "
        f"{fmt(inicio_contagem)} a {fmt(venc)}; informe-os com --feriados e recalcule.",
    ]
    quarta_cinzas = pascoa(venc.year) - timedelta(days=46)
    if inicio_contagem and inicio_contagem <= quarta_cinzas <= venc:
        avisos.append(f"Quarta-feira de Cinzas ({fmt(quarta_cinzas)}) no período: verificar expediente do tribunal.")
    if args.modo == "portal":
        avisos.append("Se o mesmo ato também foi publicado no DJEN, conferir qual regra o tribunal/STJ aplica; na dúvida, usar a data mais antiga.")

    return {
        "vencimento": venc.isoformat(),
        "vencimento_fmt": fmt(venc),
        "data_alvo_interna": alvo.isoformat(),
        "data_alvo_interna_fmt": fmt(alvo),
        "dia_do_comeco": marco.isoformat(),
        "inicio_contagem": inicio_contagem.isoformat() if inicio_contagem else None,
        "dias": dias,
        "memoria": memoria,
        "dias_nao_uteis_no_periodo": [f"{fmt(d)} — {m}" for d, m in pulados_relevantes],
        "avisos": avisos,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", required=True, help="Data do evento (AAAA-MM-DD ou DD/MM/AAAA). Ver --modo.")
    p.add_argument("--dias", required=True, type=int, help="Prazo legal em dias (sem dobrar).")
    p.add_argument("--modo", default="simples",
                   choices=["simples", "djen", "portal", "citacao-eletronica"],
                   help="simples: --data é o dia do começo (ciência/juntada); djen: --data é a disponibilização; "
                        "portal: --data é o envio ao portal (use --consulta se houve consulta); "
                        "citacao-eletronica: --data é a confirmação de recebimento.")
    p.add_argument("--consulta", help="Data da consulta no portal (modo portal).")
    p.add_argument("--dobro", action="store_true", help="Prazo em dobro (arts. 180, 183, 186, 229 CPC).")
    p.add_argument("--corridos", action="store_true", help="Contar em dias corridos (prazo de direito material).")
    p.add_argument("--feriados", help="Datas extras sem expediente, separadas por vírgula.")
    p.add_argument("--justica-federal", action="store_true", help="Incluir feriados da Lei 5.010/66, art. 62.")
    p.add_argument("--json", action="store_true", help="Saída em JSON.")
    args = p.parse_args(argv)

    r = calcular(args)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    print("MEMÓRIA DE CÁLCULO")
    for linha in r["memoria"]:
        print(f"  - {linha}")
    if r["dias_nao_uteis_no_periodo"]:
        print("Dias não úteis (exceto fins de semana) pulados:")
        for linha in r["dias_nao_uteis_no_periodo"]:
            print(f"  - {linha}")
    print(f"\nVENCIMENTO: {r['vencimento_fmt']}")
    print(f"DATA-ALVO INTERNA (2 dias úteis antes): {r['data_alvo_interna_fmt']}")
    print("\nATENÇÃO:")
    for a in r["avisos"]:
        print(f"  - {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
