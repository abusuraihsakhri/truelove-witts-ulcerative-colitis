// Modified Truelove–Witts criteria for adults; see README for clinical sources.
export function assess(input) {
  const requiredNumber = (value, field) => {
    if (value === '' || value === null || value === undefined || typeof value === 'boolean') {
      throw new Error(field + ' is required');
    }
    const number = Number(value);
    if (!Number.isFinite(number) || number < 0) throw new Error(field + ' must be a nonnegative finite number');
    return number;
  };
  const stools = requiredNumber(input.stools_per_day, 'Stools/day');
  if (!Number.isInteger(stools)) throw new Error('Stools/day must be a whole number');
  if (!['none', 'small', 'visible'].includes(input.blood)) throw new Error('Select a blood-in-stool category');
  const pulse = requiredNumber(input.pulse_bpm, 'Pulse');
  const temp = requiredNumber(input.temperature_c, 'Temperature');
  const hb = requiredNumber(input.hemoglobin_g_dl, 'Haemoglobin');
  const optionalNumber = (value, field) => value === '' || value === null || value === undefined
    ? null : requiredNumber(value, field);
  const esr = optionalNumber(input.esr_mm_h, 'ESR');
  const crp = optionalNumber(input.crp_mg_l, 'CRP');
  const toxicity = {
    pulse_over_90: pulse > 90,
    temperature_over_37_8: temp > 37.8,
    hemoglobin_below_10_5: hb < 10.5,
    esr_over_30: esr === null ? null : esr > 30,
    crp_over_30: crp === null ? null : crp > 30
  };
  const positives = Object.entries(toxicity).filter(([, met]) => met === true).map(([key]) => key);
  const sixBloody = stools >= 6 && input.blood === 'visible';
  let classification;
  let advice;
  if (sixBloody && positives.length) {
    classification = 'Severe';
    advice = 'Meets acute severe UC criteria; urgent hospital assessment is indicated.';
  } else if (sixBloody && (esr === null || crp === null)) {
    classification = 'Indeterminate';
    advice = 'Six or more visibly bloody stools/day: assess missing inflammatory markers and seek prompt clinical review.';
  } else if (stools < 4 && ['none', 'small'].includes(input.blood) && pulse < 90 &&
             temp < 37.5 && hb > 11.5 && (esr === null || esr < 20) &&
             (crp === null || crp <= 5)) {
    classification = 'Mild';
    advice = 'Mild pattern on available measures; clinical context and other investigations still matter.';
  } else {
    classification = 'Moderate';
    advice = 'Does not meet severe criteria on entered measures; clinical assessment is still required.';
  }
  return {
    classification,
    acute_severe_criteria_met: classification === 'Severe',
    systemic_toxicity: toxicity,
    positive_markers: positives,
    missing_markers: Object.entries(toxicity).filter(([, met]) => met === null).map(([key]) => key),
    clinical_recommendation: advice
  };
}
