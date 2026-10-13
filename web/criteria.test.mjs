import { test } from 'node:test';
import assert from 'node:assert/strict';
import { assess } from './criteria.mjs';
const base = { stools_per_day:3, blood:'small', pulse_bpm:75,
  temperature_c:37, hemoglobin_g_dl:13, esr_mm_h:10, crp_mg_l:2 };
const run = (overrides={}) => assess({...base, ...overrides});

test('mild and moderate classifications', () => {
  assert.equal(run().classification,'Mild');
  assert.equal(run({stools_per_day:5,blood:'visible'}).classification,'Moderate');
});
test('all five systemic markers independently trigger severe UC', () => {
  for (const change of [{pulse_bpm:91},{temperature_c:37.9},
    {hemoglobin_g_dl:10.4},{esr_mm_h:31},{crp_mg_l:31}]) {
    assert.equal(run({stools_per_day:6,blood:'visible',...change}).classification,'Severe');
  }
});
test('strict thresholds and missing inflammation markers', () => {
  assert.equal(run({stools_per_day:6,blood:'visible',pulse_bpm:90,temperature_c:37.8,
    hemoglobin_g_dl:10.5,esr_mm_h:30,crp_mg_l:30}).classification,'Moderate');
  assert.equal(run({stools_per_day:6,blood:'visible',esr_mm_h:'',crp_mg_l:''}).classification,'Indeterminate');
  assert.equal(run({stools_per_day:6,blood:'visible',pulse_bpm:95,esr_mm_h:'',crp_mg_l:''}).classification,'Severe');
});
test('invalid and missing fields are rejected', () => {
  assert.throws(()=>run({pulse_bpm:''}));
  assert.throws(()=>run({stools_per_day:3.5}));
  assert.throws(()=>run({hemoglobin_g_dl:-1}));
  assert.throws(()=>run({blood:'unknown'}));
});
