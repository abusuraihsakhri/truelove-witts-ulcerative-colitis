#!/usr/bin/env python3
"""Adult ulcerative colitis severity assessment using modified Truelove–Witts criteria.

Severe disease is >=6 bloody stools/day plus at least one systemic toxicity marker.
This is a rule-based assessment, not a weighted score or a treatment protocol.
"""
import argparse
import csv
import json
import math
import os
from pathlib import Path


def _number(value, name, *, minimum=0):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{name} must be a finite number >= {minimum}")
    return result


def assess_truelove_witts(
    stools_per_day, blood, pulse_bpm, temperature_c, hemoglobin_g_dl,
    esr_mm_h=None, crp_mg_l=None,
):
    """Evaluate adult UC severity from explicit clinical inputs.

    Thresholds use >90 bpm, >37.8 C, <10.5 g/dL, >30 mm/h ESR, and
    >30 mg/L CRP (modified criterion). Missing inflammatory markers are
    not assumed normal. When >=6 visibly bloody stools are reported and
    all available toxicity markers are negative, incomplete ESR/CRP data
    yield Indeterminate rather than an unjustified negative ASUC result.
    """
    stools = _number(stools_per_day, "stools_per_day")
    if not stools.is_integer():
        raise ValueError("stools_per_day must be a whole number")
    if blood not in ("none", "small", "visible"):
        raise ValueError("blood must be one of: none, small, visible")
    pulse = _number(pulse_bpm, "pulse_bpm")
    temp = _number(temperature_c, "temperature_c")
    hb = _number(hemoglobin_g_dl, "hemoglobin_g_dl")
    esr = None if esr_mm_h in (None, "") else _number(esr_mm_h, "esr_mm_h")
    crp = None if crp_mg_l in (None, "") else _number(crp_mg_l, "crp_mg_l")

    toxicity = {
        "pulse_over_90": pulse > 90,
        "temperature_over_37_8": temp > 37.8,
        "hemoglobin_below_10_5": hb < 10.5,
        "esr_over_30": None if esr is None else esr > 30,
        "crp_over_30": None if crp is None else crp > 30,
    }
    positives = [key for key, met in toxicity.items() if met is True]
    bloody_six = stools >= 6 and blood == "visible"
    if bloody_six and positives:
        classification = "Severe"
        advice = "Meets acute severe UC criteria; urgent hospital assessment is indicated."
    elif bloody_six and (esr is None or crp is None):
        classification = "Indeterminate"
        advice = "Six or more visibly bloody stools/day: assess missing inflammatory markers and seek prompt clinical review."
    elif (
        stools < 4 and blood in ("none", "small") and pulse < 90
        and temp < 37.5 and hb > 11.5
        and (esr is None or esr < 20)
        and (crp is None or crp <= 5)
    ):
        classification = "Mild"
        advice = "Mild pattern on available measures; clinical context and other investigations still matter."
    else:
        classification = "Moderate"
        advice = "Does not meet severe criteria on entered measures; clinical assessment is still required."

    return {
        "classification": classification,
        "acute_severe_criteria_met": classification == "Severe",
        "systemic_toxicity": toxicity,
        "positive_markers": positives,
        "missing_markers": [key for key, value in toxicity.items() if value is None],
        "clinical_recommendation": advice,
    }


def calculate_metrics(**kwargs):
    """Backwards-compatible function name; now requires named UC observations."""
    return assess_truelove_witts(**kwargs)


def process_batch(input_csv, output_csv):
    """Evaluate a CSV with the same named columns as assess_truelove_witts."""
    if not os.path.isfile(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    if Path(input_csv).resolve() == Path(output_csv).resolve():
        raise ValueError("Output CSV must differ from input CSV")
    required = {"stools_per_day", "blood", "pulse_bpm", "temperature_c", "hemoglobin_g_dl"}
    with open(input_csv, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        if len(fields) != len(set(fields)) or not required.issubset(fields):
            raise ValueError("CSV requires unique headers: " + ", ".join(sorted(required)))
        output = []
        for line, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {line} has extra columns")
            try:
                result = assess_truelove_witts(**{k: row.get(k) for k in
                    (*sorted(required), "esr_mm_h", "crp_mg_l")})
            except ValueError as exc:
                raise ValueError(f"CSV row {line}: {exc}") from exc
            row = dict(row)
            row.update({
                "classification": result["classification"],
                "acute_severe_criteria_met": str(result["acute_severe_criteria_met"]),
                "positive_markers": ";".join(result["positive_markers"]),
                "clinical_recommendation": result["clinical_recommendation"],
            })
            output.append(row)
    output_fields = [x for x in fields if x not in
        ("classification", "acute_severe_criteria_met", "positive_markers", "clinical_recommendation")]
    output_fields += ["classification", "acute_severe_criteria_met", "positive_markers", "clinical_recommendation"]
    with open(output_csv, "w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=output_fields)
        writer.writeheader()
        for row in output:
            # Prevent untrusted spreadsheet values from being interpreted as formulas.
            writer.writerow({k: ("'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v)
                             for k, v in row.items()})
    print(f"Processed {len(output)} records -> {output_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Adult UC modified Truelove–Witts assessment")
    subs = parser.add_subparsers(dest="command", required=True)
    single = subs.add_parser("single", help="Assess one adult UC case")
    single.add_argument("--stools-per-day", type=int, required=True)
    single.add_argument("--blood", choices=("none", "small", "visible"), required=True)
    single.add_argument("--pulse-bpm", type=float, required=True)
    single.add_argument("--temperature-c", type=float, required=True)
    single.add_argument("--hemoglobin-g-dl", type=float, required=True)
    single.add_argument("--esr-mm-h", type=float)
    single.add_argument("--crp-mg-l", type=float)
    batch = subs.add_parser("batch", help="Assess cases from CSV")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    try:
        if args.command == "single":
            values = vars(args).copy()
            values.pop("command")
            print(json.dumps(assess_truelove_witts(**values), indent=2))
        else:
            process_batch(args.input, args.output)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
