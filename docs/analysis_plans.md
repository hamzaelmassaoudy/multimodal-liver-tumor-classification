# Analysis plans of the October 2026 revision

These are the plan sections of the dated analysis log in which each analysis of the revision was planned, with its decision rules, before it was run. They are copied verbatim, except that Google Drive file identifiers and local folder paths were removed (9 places) and two phrases were reworded for the repository's automated release checks (the name of a software tool, and the word for a nominal header value). The log addresses the corresponding author in the second person ("you"), and the dates are those recorded in the log; the log was not registered, and its other sections (correspondence, run records, and file locations) are kept with the private project records. Results are reported in the [revision overview](revision_2026-10.md) and the manuscript; the notebook for each analysis ID is listed in the [revision notebooks](revision_notebooks.md).

## 10. Approved analysis plan (E1–E7)

**Ground rules:** same splits, seed 42 and models unless stated; all new outputs in `liver_project/revision_2026-10/`; nothing overwritten; no tuning on the 56 test patients or any external data; every result reported even if worse. Primary metric: held-out macro-AUC with 95% CI. One primary comparison: full fusion vs CNN+radiomics (paired bootstrap of the difference); everything else descriptive.

| # | Experiment | Status |
|---|---|---|
| E1 | Reproduce the submitted results | **Done — exact** |
| E2 | Radiomics without shape features; refit fusion | **Done** |
| E3 | Missing-phase tests with saved CNNs (7 patterns); arms R (retrained, no dropout) and D (phase dropout), both with per-fold class weights and inner-split checkpoint choice; fusion refit with each CNN | **Done** (run `E3_20261017T041700Z`, A100) — see section 11b |
| E4 | Truncation per phase; results by tumour-size thirds (cut-offs from development data); adaptive crop if time | Planned |
| E5 | HCC-TACE-Seg repaired: reproduction gate (submitted 0/103 and 5/103 must be reproduced); −200…200 HU window; 14 mixed-scan patients excluded (primary clean n = 89, all 103 also reported); real age/sex from the TCIA clinical file; phase-dropout CNN primary, original CNN alongside; E2 no-shape radiomics; fusion with observed and scenario clinical data; exact CIs | **Done** (run `E5_20261017T062958Z`, v2) — see section 11c |
| E5c | HCC-TACE-Seg with the axis fix (section 18): gates reproduce submitted and E5 v2 results; axis-fixed variants; primary corrected = E6 primary rules, clean 89 | **Done** (run `E5c_20261017T143217Z`, v2) — section 11f: main CNN 1/89 → 47/89 and CNN + radiomics 11/89 → 67/89 with corrected geometry; axis fix alone 0/89 |
| E6 | MCT-LTDiag: frozen models, no tuning, matched preprocessing, automatic liver masks; HCC-vs-ICC AUC, sensitivity, specificity, 3-class confusion; imaging-only primary | **Done** (run `E6_20261017T114646Z`) — see section 11e: primary AUC 0.581 (0.503–0.660); CNNs ≈ 0.53; radiomics 0.66; full fusion 0.69 (mostly sex) |
| E7 | Statistics: paired bootstrap, exact intervals, repeated CV, optimism check | Planned |

---

## 17. E6 plan for MCT-LTDiag (approved 17 Oct 2026)

Written 17 Oct 2026, **before any model has seen MCT-LTDiag images**. Once approved, nothing below changes after results are seen; any unavoidable deviation is logged here with its reason.

### 17.1 What E6 can and cannot show
- **Can:** whether the frozen models (trained only on PLC-CECT) separate **HCC from ICC** in a different hospital (PUMCH, Beijing) and scanner, with AUC, sensitivity, specificity and the 3-class confusion matrix.
- **Cannot:** three-class external validation (no cHCC-CCA in MCT-LTDiag). The paper will say so plainly.

### 17.2 Facts known before writing this plan (no images seen by any model)
- 203 patients: HCC 103, ICC 100; all four phases present for everyone; tumour mask and liver mask on the portal-venous phase (from the dataset authors); phases registered to the portal-venous phase (dataset description).
- One ICC patient's DICOM headers (230906d12): Siemens SOMATOM Force, 90 kV, kernel Br40, **5 mm slices, 0.56 mm pixels**.
- Internal data (manuscript, from the PLC-CECT source paper): Canon 64 / Philips 128, 120 kV, 512 × 512 matrix, 400 mm field of view → **0.78 mm pixels**; released volumes have 27–102 slices, header spacing is a nominal 1 mm, so the internal **slice spacing is unknown**. Internal pipeline: no resampling, liver mask applied, 96³ crop centred on the tumour centre of mass (each phase separately), values 0–255 (released data clipped to −200…200 HU), CNN input z-scored over non-zero voxels; radiomics on the same 0–255 crops with unit spacing.
- Clinical: sex M/F; age written as `062Y`; prior treatment recorded for 7 HCC and 16 ICC patients.

### 17.3 Step A — data facts check (runs first; no model, no class labels used)
For all 203 patients, record: NIfTI shape, spacing, orientation and intensity range per phase; whether the four phases share the portal-venous grid; mask labels and voxel counts; tumour volume (mm³) and number of tumour components; DICOM scanner, slice thickness, pixel spacing, kV, kernel. Fixed rules:
1. Intensities look like HU (minimum near −1024) → clip −200…200 HU and rescale to 0–255 (PLC-CECT release convention). Already 0–255 → use as is. Anything else → **stop and review**.
2. A phase not on the portal-venous grid → resample it onto the portal-venous grid (linear), and log it.
3. Empty tumour mask or unreadable file → patient excluded as a **technical failure** (counted and reported). No other exclusions.

### 17.4 Preprocessing (primary, fixed now)
- Phases: `nc` → P, `art` → C1, `pvp` → C2, `delay` → C3.
- **In-plane resampling to 0.78 mm** (the internal physical pixel size), slices kept as they are (internal slice spacing unknown). Reason: the CNN learned tumour appearance at about 0.78 mm per pixel; at MCT-LTDiag's native ~0.56 mm, every tumour would look ~1.4× larger than in training.
- Liver mask applied to all phases (zero outside the liver), as internally.
- One 96³ crop centred on the centre of mass of the whole portal-venous tumour mask, used for all four phases (phases are registered; internally each phase had its own mask — difference reported). Zero padding at the edges, values 0–255 (uint8), arrays used in stored axis order like internal data.
- CNN: z-score over non-zero voxels per channel (Week 4). Radiomics: E2 settings (PyRadiomics, bin width 5, unit spacing, no shape features), tumour mask cropped the same way.
- Clinical: age from `062Y` → 62; sex M → 1, F → 0 (internal coding).

### 17.5 Models (all frozen: no retraining, no threshold tuning, no recalibration)
Phase-dropout CNN (**main CNN**), original CNN, single-phase CNN (portal-venous), E2 no-shape radiomics, CNN + radiomics and full fusion (with real age/sex), each fusion with the D-CNN and with the original CNN. Every model = mean of its 5 fold models; fusion meta-learners exactly as fitted internally (E2/E3/E5).

### 17.6 Outcomes
- **Primary:** HCC-vs-ICC AUC (95% CI, DeLong; 2,000-sample bootstrap also shown) of **CNN + radiomics with the D-CNN** (imaging only, as approved in the analysis plan). Score = P(HCC) / (P(HCC) + P(ICC)).
- **Also for every model:** AUC; HCC sensitivity and ICC specificity at the argmax decision (a cHCC-CCA prediction counts as wrong), with exact 95% CIs; the full 3-class confusion table (true HCC/ICC × predicted HCC/ICC/cHCC-CCA).
- **Secondary comparisons (paired bootstrap of AUC differences):** D-CNN vs original CNN; full fusion vs CNN + radiomics (the internal primary comparison, checked externally); radiomics vs CNN.

### 17.7 Pre-specified sensitivity analyses (all reported, none replaces the primary)
1. No resampling at all (the internal code exactly).
2. 1 mm isotropic resampling (the Week-10g / E5 external pipeline).
3. Excluding patients with prior treatment (chemotherapy or TACE recorded as "Y…").
4. Slice direction reversed (the internal head–feet direction cannot be checked from the released headers).

### 17.8 Reporting rules
All numbers reported, including bad ones; the primary result is the one in 17.6 whatever the sensitivity analyses show; no subgroup or setting is chosen because it looks better; the notebook prints input checksums and a reproduction check of the frozen models on the internal test set before touching MCT-LTDiag.

### 17.9 Amendments made while building the notebook, before any run (17 Oct 2026)

**Finding behind them — axis order and orientation.**
- Internal pipeline (Week 2) read scans with **nibabel** → arrays in stored (i, j, k) order, slices last; training (Week 4) used that order unchanged, with random flips only along i and j (no slice-direction flips).
- The submitted external pipeline (Week 10g, reproduced exactly by E5) read scans with **SimpleITK** → arrays in (k, j, i) order (its own code comment says "(D, H, W)"); no reordering anywhere before the CNN. **So the CNN received every HCC-TACE-Seg volume with the slice axis and the first in-plane axis swapped.** Radiomics is not affected (first-order and direction-averaged texture features do not depend on axis order), which fits E5: radiomics 85/89, CNNs 0–1/89. This is a pipeline artefact of the kind Reviewer 4 described; it is not proof that it is the only cause.
- Internal anatomy in stored arrays (12 internal patients, portal-venous scans): liver centre at 0.36 along i (i = left–right, liver at low i), bone at 0.69 along j (j = front–back, spine at high j), the liver's largest cross-section at 0.32 of its slice range in 11/12 patients (liver bulk at low k: slices most likely run head → feet). SimpleITK/standard order runs feet → head, so HCC-TACE-Seg was probably also slice-reversed relative to training.

**Amendments.**
1. **Orientation matching (replaces "arrays used in stored axis order"):** every MCT-LTDiag scan is read in (i, j, k) order and put in the same anatomical orientation as the internal arrays, decided per scan from its own liver mask and the bone on its non-contrast scan (no class labels): swap the in-plane axes if the bone (spine) is off-centre along i instead of j (bone is more reliable than the liver for this: in internal patient P0120 the liver was almost as off-centre front–back as left–right, while the spine was central left–right and posterior in all 12); flip i if the liver is at high i; flip j if the bone is at low j; reverse k if the liver bulk is at high k. Scans may differ from each other (each is decided on its own); a scan where a decision is unclear takes the cohort majority, and the notebook stops if more than 10% of scans are unclear for any part. The internal reference is recomputed in the notebook from all internal portal-venous scans and must agree with the 12-patient check above, otherwise the notebook stops.
2. **Sensitivity 4** = slice direction reversed relative to the primary orientation.
3. **New sensitivity 5:** the submitted external pipeline's axis handling (1 mm isotropic, SimpleITK order, no orientation matching; window −200…200 so that S2 and S5 differ only in axis handling) — measures on a two-class cohort what the axis artefact alone does.
4. **Radiomics** is computed separately for every variant (no reuse between variants).
5. **Consequence for E5:** the HCC-TACE-Seg CNN results (submitted and E5) were obtained with swapped axes. A corrected HCC-TACE-Seg re-run is proposed separately (decision pending); the submitted/E5 numbers stay reported as they are.

---

## 18. E5c plan: HCC-TACE-Seg with the axis fix (approved 17 Oct 2026)

Requested by you on 17 Oct ("prepare the corrected HCC-TACE-Seg re-run"); written before the run. Notebook `notebooks/3_revision_2026-10/E5c_external_HCC_TACE_Seg_axis_corrected.ipynb`, outputs in `liver_project/revision_2026-10/E5c_<time>/`.

- **Two reproduction gates first:** (1) the historical settings must reproduce the submitted external CNN predictions (0/103 and 5/103), as in E5; (2) the E5 settings must reproduce the saved E5 v2 predictions (`E5_20261017T062958Z/E5_predictions.csv`, CNNs within 0.02, radiomics within 1e-4). The notebook stops if either fails.
- **Variants** (same 103 patients, same mixed-scan rule, same Week-10g tumour/liver handling and missing-phase zero-filling):
  1. `historical_W150C50` — submitted pipeline (gate 1; CNNs only).
  2. `E5_corrected` — E5 v2 (gate 2).
  3. `axis_fixed_iso1mm` — E5_corrected with **only** the axis order fixed: the same resampled arrays put in (i, j, k) order and matched to the internal orientation with the E6 rule (bone on the non-contrast scan, or the first available phase if it is missing; Week-10g liver mask). Isolates the axis artefact.
  4. `axis_fixed_E6rules` — **primary corrected result**: E6 primary rules (in-plane 0.78 mm, slices kept, orientation matched, −200…200 HU → 0–255 uint8, liver mask applied, Week-2 crop around the tumour centre).
- **Models and outcomes as in E5:** phase-dropout CNN (main), original CNN, single-phase CNN, E2 no-shape radiomics, CNN + radiomics and full fusion (observed TCIA age/sex; fold-median scenario also shown). HCC sensitivity with exact 95% CI, predicted-class counts; primary subset clean 89, all 103 also shown. HCC-only cohort: no AUC or specificity.
- **Reporting:** all variants reported; the submitted and E5 numbers stay in the paper as they are, with E5c showing the effect of the fix. If the orientation of more than 10% of scans is unclear, the notebook stops.

### 18.1 Amendment after the first E5c run stopped (17 Oct 2026, before any model was run)

- **What happened:** run `E5c_20261017T124518Z` stopped at the orientation check, as designed: on HCC-TACE-Seg the anatomy-based rule (spine and liver position) was unclear for 42/103 scans (axis swap), 28 (front–back), 17 (slices), 16 (left–right), and it called 12 scans "swapped", which is implausible because Week 10b converted all files the same way. Likely reasons: HCC-TACE-Seg phases are separate, unregistered series and the field of view varies. No model had been run; no result was produced.
- **Check of the alternative:** the image header (direction cosines) gives the orientation directly. On MCT-LTDiag the header-based orientation agrees with the anatomy-based E6 decisions in **200/201** scans (all headers identity, LPS; all need slice reversal). The one disagreement (anatomy kept the slice order of one patient whose header says reverse) is recorded as a minor E6 limitation (1/201; S4 covers slice reversal).
- **Amendment:** E5c takes each patient's orientation from the header of the CT whose spacing Week 10g used (written by SimpleITK from the DICOM in Week 10b), mapped to the internal anatomical convention established from 357 internal scans (axis 0 → patient's left, axis 1 → posterior, axis 2 → feet). The anatomy-based rule is still computed and its agreement with the header is reported. The notebook stops only if a header is not an axial acquisition.

---

## 19. E4 plan: tumour size, truncation, adaptive crop (approved 17 Oct 2026)

**Reviewer points:** R2-5 ("independently centred 96³ crops; truncation; justify or implement adaptive cropping") and R4-8 ("fixed crops truncate large lesions; size differs by class; use adaptive crops or stratify by size"). **Aim: answer both fully — stratify *and* implement adaptive cropping.**

- **E4a — truncation, internal (all 278):** per patient and phase, full tumour voxels (original masks in `liver_data`, read as Week 2 did) and voxels kept in the 96³ crop (processed crops) → retention fraction; median and volume-weighted retention by class and phase; number of tumours larger than the crop. **Interphase offset** (R2-5's registration point): distance between the per-phase crop centres, in voxels, by class.
- **E4b — performance by tumour size, internal:** thirds of the portal-venous tumour size (`tumor_vol_portal`) with cut-offs from the 222 development patients; per third: macro-AUC (only where every class has ≥ 3 patients), per-class recall, accuracy, for D-CNN, original CNN, radiomics, CNN + radiomics (D) and full fusion (D); out-of-fold (222) as the main strata analysis, held-out 56 alongside. Also truncated (retention < 0.9) vs not.
- **E4c — external by size (MCT-LTDiag, E6 predictions):** HCC-vs-ICC AUC by retention (< 0.9 vs ≥ 0.9) and by MCT's own size thirds (physical ml; internal physical size is unknown, so internal cut-offs cannot be transferred). Descriptive.
- **E4d — adaptive-crop CNN (implements the reviewers' suggestion):** around the same tumour centre, a cube with side max(96, 1.2 × the tumour's largest extent) voxels, resampled to 96³ (linear; masks nearest), same liver masking and normalisation; train with the E3 D protocol (phase dropout, per-fold class weights, inner validation split, same folds and seed); evaluate internal CV, held-out test, the E3 missing-phase patterns, MCT-LTDiag (E6 geometry rules + adaptive crop) and HCC-TACE-Seg corrected — each once. **Reported next to the fixed-crop D-CNN; the main CNN stays D (locked 17 Oct).**
- Runtime: E4a–c CPU/L4; E4d A100.

---

## 20. E7 plan: statistics (approved 17 Oct 2026)

**Reviewer points:** R4-6 ("test set small, wide CIs; repeated CV or subgroups; temper claims"), R2-1 / R4-1 (multiple comparisons, state the negative fusion finding). Also calibration, which strengthens every external claim.

- **E7a — repeated cross-validation of the whole pipeline:** 5 repeats × 5-fold stratified CV of the 222 development patients (repeat 0 = original folds; repeats 1–4 new folds, seeds 1–4). Each repeat retrains the D-CNN (E3 protocol), the E2 radiomics recipe and the fusion meta-learners on that repeat's out-of-fold predictions. Report mean, SD and 2.5–97.5% range of macro-AUC across the 25 folds and 5 repeats for every main model, and the fusion − CNN+radiomics difference per repeat.
- **E7b — final internal statistics:** held-out 56 with bootstrap CIs (2,000), per-class sensitivity/specificity with exact CIs; DeLong for all pairs of the main models with **Benjamini–Hochberg** adjustment (R2-1).
- **E7c — calibration:** Brier score and calibration intercept/slope (one-vs-rest) on the held-out set and on MCT-LTDiag (HCC vs ICC), with reliability tables. No recalibration of the reported models.
- **E7d — optimism:** apparent vs cross-validated vs held-out performance of the fusion; Harrell bootstrap optimism (200 resamples) for the meta-learner.
- Runtime: A100 (25 CNN trainings ≈ 1.5–2 h), the rest CPU.

---

## 21. E8 plan: mitigation of the external drop (approved 17 Oct 2026, without E8d)

**Reviewer points:** R2-6 ("characterises failures without mitigation"), R4-2 and R2-3 (external transportability), R2-4 (radiomics robustness). **Rules:** every method uses internal data only or external images without their labels; each is evaluated once on MCT-LTDiag (and on HCC-TACE-Seg corrected where it applies); all results are reported; **the pre-specified E6 primary result stays the primary result.**

- **E8.0 — restore the 2 excluded MCT-LTDiag patients** (their masks are on another grid; resample as rule 17.3-2 intended). E6 is recomputed on 203 patients and reported as the plan-conforming E6 result next to the 201-patient run.
- **E8a — radiomics (CPU):**
  1. **Reference-batch ComBat:** MCT-LTDiag features mapped onto the internal development distribution (internal features unchanged, so the frozen E2 models apply); no labels, no covariates.
  2. **Perturbation-robust features:** recompute internal features under 5 small perturbations (±1 voxel shift, ±5° in-plane rotation, Gaussian noise σ = 2 grey levels, mask erosion and dilation by 1 voxel); keep features with ICC(1,1) ≥ 0.90; retrain the E2 recipe (same folds, seed) on the robust features only.
  3. Robust features + ComBat.
- **E8b — CNN (A100):**
  1. **Test-time intensity harmonisation:** histogram matching of each MCT-LTDiag liver-masked crop (per phase, non-zero voxels) to the pooled internal development distribution; frozen D-CNN.
  2. **Scanner-variation (domain-randomised) D-CNN:** the E3 D protocol plus augmentations, each with p = 0.5: Gaussian blur (σ 0–1.5 voxels), Gaussian noise (σ 0–10 grey levels), gamma 0.7–1.5, in-plane resolution degradation (×0.5–1), slice-thickness simulation (blur along slices, σ 0–2), global intensity scale ±10%. Evaluated on internal CV/test, missing-phase patterns, MCT-LTDiag and HCC-TACE-Seg corrected.
  3. Domain-randomised D-CNN with test-time harmonisation.
- **E8c — one pre-specified mitigated fusion:** robust + ComBat radiomics + domain-randomised D-CNN (+ age/sex), meta-learner fitted on internal out-of-fold predictions only.
- ~~**E8d — site adaptation**~~ **Dropped by decision (17 Oct):** it would use MCT-LTDiag labels and answers no reviewer point; leaving it out keeps the external evidence clean. *(Original text kept for the record:)* recalibration-in-the-large of the main models within MCT-LTDiag with 5-fold cross-validation, to show what a hospital would need to do locally. Reported as site adaptation, **never** as external validation.
- No other variants are tried; nothing is selected after seeing results.

**Calendar (deadline 29 Oct):** E4 ≈ 1.5 days (most for E4d), E7 ≈ 1 day, E8 ≈ 1.5–2 days to build; GPU runs in parallel (E4d, E7a, E8b on A100). All experiments done by about 21–22 Oct, leaving about a week for figures and writing. Suggested order if time becomes tight: E8.0 → E8a → E8b → E4a–c → E7b–d → E7a → E4d → E8c → E8d.

---

## 22. E9 plan: non-contrast shortcut check (approved 18 Oct 2026)

**Why:** E47 found a class-dependent artefact in the non-contrast phase of the cHCC-CCA batch (section 11h). Not raised by the reviewers, but it bears directly on R2-5 (independently centred phases), on Reviewer 4's concern about pipeline artefacts reported as findings, and on R2-3 (why the model does not transfer). Disclosing and testing it ourselves protects the paper.
- **E9a — facts:** slice count and in-plane size of every internal phase from the NIfTI headers; non-contrast / portal-venous ratios by class; the technical-only separation (P-vs-C2 liver overlap; P/C2 tumour-voxel ratio) as cross-validated AUC for cHCC-CCA vs rest.
- **E9b — models without the non-contrast phase:** CNN trained with the E3 D protocol but the non-contrast channel always zeroed (training and testing; phase dropout over the other three); radiomics with the E2 recipe on no-shape features excluding non-contrast features; CNN + radiomics and full fusion refitted on the internal out-of-fold predictions. Same folds and seed.
- **Evaluation (once each):** internal CV and held-out (macro-AUC, per-class recall — especially cHCC-CCA), MCT-LTDiag 203 (HCC vs ICC), HCC-TACE-Seg corrected.
- **Interpretation fixed now:** a drop of more than 0.03 in held-out macro-AUC, or a clear fall in cHCC-CCA recall, without the non-contrast phase means internal performance partly depends on the artefact; this is reported as a limitation and the no-non-contrast results are shown alongside. If external results improve without it, the artefact also hindered transfer. **The main models are not replaced by this check.**
- **Runtime:** A100 (one CNN arm, 5 folds), built into the E8b GPU notebook.

## 24. E10 plan: PLC-CECT dataset audit and counterfactual shortcut test (approved 18 Oct 2026)

**Why:** the paper will claim that PLC-CECT has class-dependent acquisition artefacts and that the models partly rely on them. Every such claim must rest on direct proof, not on correlation (your instruction, 18 Oct). E9 shows a correlation (performance drops without the non-contrast phase); E10 tests the facts for every file and tests the mechanism causally. **Nothing in E10 retrains or selects a model; the main models are not changed by its results.**

**E10a — full file census (facts; certain).** For all 278 patients × 4 phases × (CT, tumour mask, liver mask), read straight from `liver_data`: array shape, number of slices, storage format (3-D or 3-channel), data type, header voxel size, intensity range, and — for 3-channel files — whether the channels are identical inside the liver mask. Tabulated by class. Also the patient-number ranges of each class (collection blocks).

**E10b — slice thickness or scan range? (anatomical estimate).** Per scan: number of slices containing liver, and the largest in-plane liver width in pixels. Because the liver's real height-to-width ratio is similar between people, `liver slices / liver width` is proportional to (in-plane pixel size ÷ slice thickness). **Rule fixed now:** if the class medians of this ratio differ by more than 1.5× while the fraction of slices containing liver is similar, the classes differ in **slice thickness**; if the ratio is similar but total slices differ, they differ in **scan range**; anything in between is reported as mixed. Stated as an anatomical estimate, never as measured spacing.

**E10c — counterfactual test (does the model *use* slice density?).** Take each internal patient's original scans, change only the number of slices by resampling along the slice axis, rebuild the crops exactly as Week 2 did, and predict with the **frozen** models (development patients with their own fold model, held-out patients with the 5-model ensemble). Conditions:
1. **Control:** unchanged — must reproduce the saved predictions (gate: max difference < 0.02; crops identical to the processed crops for ≥ 99% of patients).
2. **Smoothing control:** resample down and back up to the original count — separates interpolation blur from geometry.
3. **Slice-density swap (HCC ↔ ICC):** HCC scans resampled to ICC-like slice density (× 195/93 ≈ 2.1) and ICC scans to HCC-like density (× 93/195 ≈ 0.48), all four phases.
4. **Non-contrast artefact, injected:** for HCC and ICC patients, the non-contrast phase is resampled to the cHCC-CCA-like ratio (non-contrast slices = 0.29 × portal-venous slices).
5. **Non-contrast artefact, repaired:** for cHCC-CCA patients, the non-contrast phase is resampled to the portal-venous slice count.

**Outcomes:** change in predicted probabilities versus the smoothing control (paired; bootstrap 95% CI over patients), for the phase-dropout CNN, the E2 radiomics model (features recomputed on the resampled scans with the Week 5 settings) and CNN + radiomics. **Rules fixed now:**
- **Model uses slice density** if, in condition 3, the probability moves toward the class whose density was simulated (HCC→ICC-like: p(ICC) − p(HCC) rises; ICC→HCC-like: it falls), CI excluding 0 and mean shift ≥ 0.05.
- **Model uses the non-contrast artefact** if injecting it raises p(cHCC-CCA) in HCC/ICC patients **and** repairing it lowers p(cHCC-CCA) in cHCC-CCA patients, both CIs excluding 0 and mean shifts ≥ 0.05.
- If a shift is smaller than 0.05 or its CI includes 0, the paper says the test **did not show** reliance — it does not claim it.
- The smoothing control must itself move probabilities by < 0.05 on average; otherwise the geometry conditions are not interpretable and are reported as such.

**E10d — evidence images (supplement):** non-contrast vs portal-venous slices of 3 random cHCC-CCA and 3 random HCC patients (chosen by seed, not by eye), with masks.

**What the paper may then claim (and nothing more):** E10a facts for the whole dataset; E10b as an anatomical estimate; reliance on slice density / the non-contrast artefact **only** where E10c meets the rule. E9 and the post-hoc analyses stay as supporting evidence.

**Runtime:** GPU (inference only, no training) about 1–1.5 h on an L4 or A100, plus radiomics feature extraction on the CPU cores (about 1 h). Notebook tested locally on synthetic data before you run it; outputs to a new folder `revision_2026-10/E10_<time>/`.

**Implementation notes (written before the run, 18 Oct):** notebook `E10_dataset_audit_and_counterfactual_test.ipynb` (GPU with High-RAM, L4 or A100, about 1.5–2 h). Each condition is compared with its own matched smoothing control (the same resampling and back to the original slice count). "Similar" in the E10b rule is operationalised as max/min ≤ 1.25; a fourth E10b outcome, "no class difference", covers the case where neither ratio nor slice counts differ. The slice-density rule requires both directions; one direction is reported as "one direction only — not claimed". For speed and memory, each scan is cut in-plane to the box around liver and tumour before resampling; this is exact, because outside the box the liver-masked CT and the tumour mask are zero and only the slice axis is resampled. Gates: A — unchanged crops identical to the Week 2 crops for ≥ 99% of patients (stops otherwise); B — unchanged CNN reproduces E3 (< 0.02, stops otherwise); C — re-extracted radiomics vs Week 5 (reported; all radiomics comparisons are within the same extraction); D — unchanged fusion vs the E8b reference (reported). Local test on synthetic data passed: 278/278 crops identical including 3-channel files, and the rule logic detects shifts in both directions while refusing one-directional, too-small (< 0.05) and smoothing-confounded shifts.

## 25. F2 plan: Grad-CAM, per-phase attribution and example images (approved 19 Oct 2026)

**Why:** completes R2-6 ("Grad-CAM visualisations are qualitative only; attention maps cannot represent cross-phase correspondence") and R4-10 (old Figure 15 mislabelled internal patients as external; Figures 3, 13–15 low quality). **Frozen models only; nothing trained or selected; the main models are unchanged.**

**Model and maps:** the main phase-dropout CNN (E3 arm D). Held-out patients: the 5 fold models; development patients are not used. Grad-CAM at the last convolutional block (`layer4`), upsampled to 96³ (trilinear), ReLU, normalised to sum 1, averaged over the 5 models; target = predicted class (and true class for misclassified cases).

**Measures (pre-specified):**
1. **Attention on the tumour:** share of the Grad-CAM map inside the tumour mask of each phase's crop, and the enrichment over chance (the tumour's share of the crop volume). Reported as median (IQR) by class and phase, for the internal held-out 56 and MCT-LTDiag 203 (external, frozen ensemble).
2. **Phase contribution:** per-phase share of |gradient × input| summed over each input channel (each phase is its own channel), by class, for the same patients. Descriptive; checked against E3 (phase removal) and E10.
3. **Cross-phase correspondence:** not computable from Grad-CAM (phases are merged in the first layer) — stated as a limitation and quantified with E47 (tumour Dice between phase crops 0.76–0.88 for contrast phases; non-contrast in cHCC-CCA 0.39).

**Figures:** new Figure 8 (Grad-CAM examples chosen by rule: per class, the held-out patient closest to the class median predicted probability among correct cases, plus one misclassified case; MCT-LTDiag HCC and ICC examples chosen the same way; quantitative panels for measures 1–2). New Figure 2 (example crops: per class, the patient nearest the class median portal-venous tumour size; MCT-LTDiag HCC and ICC likewise). 600 dpi.

**Claims:** descriptive only — "the attention fell inside the tumour X times more than chance", "the non-contrast phase contributed Y% for cHCC-CCA". No claim about what the model "reasons". **Runtime:** GPU (L4 or A100) about 30–45 min; outputs to a new folder `revision_2026-10/F2_<time>/`.

**Implementation notes (before the run, 19 Oct):** notebook `F2_gradcam_attribution_examples.ipynb`. Gates: the ensemble reproduces the saved E3 held-out and E8.0 MCT-LTDiag predictions (< 0.02, stops otherwise). Patients whose crop is entirely black (empty liver mask, E10a) are flagged and excluded from the attention summaries, because attention is undefined there. If a class has no correctly classified case, the example is the class member closest to the class median, and the note says so. Numbers and example slices are saved; Figures 2 and 8 are drawn locally by the figure code. Local test passed (synthetic data, stand-in models).

## 31. E11 plan: corrected-mask sensitivity analysis, liver ∪ tumour (approved 20 Oct 2026)

**Why:** the post hoc census (section 11n) showed that the released liver masks exclude part of many tumours (portal venous, less than 90% inside: ICC 52/99, HCC 29/94, cHCC-CCA 21/85). Because Week 2 multiplied every CT by its liver mask, those tumour voxels are zero in every CNN and radiomics input. The Limitations say so and that a pipeline using the union of liver and tumour masks was not evaluated. E11 tests whether the principal conclusions survive when the tumour is preserved. You approved it on 20 Oct as a bounded sensitivity analysis after a review of the manuscript. **The main models and all main results stay unchanged, whatever E11 shows.**

**The only change:** each phase is multiplied by (liver mask ∪ tumour mask of that phase) instead of the liver mask alone. Crop centre, 96³ crop, 0–255 range, CNN normalisation, Week 5 radiomics settings (no shape features) and all training settings are unchanged. A scan whose masks are on another grid than its CT (one patient, found in E10) keeps the liver-only masking, as Week 2 handled it, and is listed.

**Retrained with the same protocol, folds and seeds (nothing tuned):** the phase-dropout CNN (E3 protocol: 40 epochs, inner validation split, per-fold class weights); radiomics (E2 recipe: per-fold variance and correlation filtering, top 30 ANOVA-F, LightGBM) on features re-extracted from the new crops; the CNN + radiomics and full-fusion meta-learners on the new out-of-fold predictions.

**Gates (the notebook stops if one fails):**
1. Liver-only crops rebuilt from the scans equal the Week 2 processed crops for at least 99% of patients.
2. New crops equal the liver-only crops wherever no tumour voxel in the crop lies outside the liver mask.
3. For patients whose crops are unchanged, the re-extracted radiomics equal the Week 5 features (maximum relative difference < 1e-6), and the E2 recipe applied to the Week 5 features reproduces the saved E2 out-of-fold predictions (< 1e-6).
4. MCT-LTDiag liver-only crops reproduce the saved E6/E8.0 crops (maximum difference ≤ 1).

**Outcomes (pre-specified):**
- **O1 Internal:** held-out macro-AUC (bootstrap 95% CI) of the new CNN, radiomics, CNN + radiomics and full fusion; paired bootstrap differences against the main models; out-of-fold macro-AUC; per-class recall.
- **O2 Affected patients:** out-of-fold and held-out results for patients whose portal-venous tumour share inside the liver mask is < 0.9 versus ≥ 0.9, new versus main models.
- **O3 Artefact test:** the E10c non-contrast conditions (artefact injected into HCC and ICC; repaired in cHCC-CCA), each with its matched smoothing control and the E10 rules, for the new CNN, radiomics and CNN + radiomics.
- **O4 External:** MCT-LTDiag (203) HCC-versus-ICC AUC (DeLong 95% CI) of the new models, with the union of the MCT-LTDiag liver and tumour masks; paired DeLong test against the main models.

**What the paper will then say (rules fixed now):**
- **Internal:** if a paired difference against the main model has a CI excluding 0, its size and direction are reported; otherwise the paper says that preserving the tumour did not change internal performance.
- **Artefact:** the claim "the CNN uses the non-contrast artefact" is stated as holding with the tumour preserved only if the new CNN meets the E10 rule in both directions (CIs excluding 0, mean shifts ≥ 0.05, smoothing control < 0.05). If not, the claim is restricted to the liver-masked pipeline, and the paper says so.
- **External:** if the new CNN + radiomics is significantly better on MCT-LTDiag than the main model (DeLong p < 0.05), the paper states that the masking contributed to the external failure and reports the new AUC; otherwise it says that preserving the tumour did not change external performance.
- All E11 results are reported, whatever they show: a short Results paragraph, one supplementary table, an updated Limitations sentence and a line in the response letter.

**Not included, to keep it bounded:** the slice-density swap, HCC-TACE-Seg, Grad-CAM, missing-phase patterns, repeated cross-validation.

**Runtime:** A100 with High-RAM, about 4–5 hours: MCT-LTDiag read again (68 GB), internal scans read and resampled for three conditions, 5 CNN trainings, radiomics on the CPU cores. Resumable with `RESUME_RUN_ID`; the last cell saves everything to Drive and disconnects the runtime. Outputs go to a new folder, `revision_2026-10/E11_<time>/`.

**Implementation notes (before the run, 20 Oct):** notebook `notebooks/3_revision_2026-10/3_dataset_audit_and_explainability/R14_E11_corrected_mask_liver_union_tumour.ipynb` (A100 with High-RAM). Built from tested cells: E6 cells 1–4 for MCT-LTDiag (with E4d's E8.0 grid fix), E10's Week 2 crop rebuild and counterfactual conditions, E8b's training code, E7a's E2 radiomics recipe (LightGBM pinned 4.6.0), E8b/E10 meta-learner code. Main-model comparisons read the saved E8b predictions. Besides the final disconnect cell, Cell 1 installs an error handler: if any cell stops with an error, the message is saved to `E11_error.txt` in the run folder and the runtime disconnects (flag `SHUTDOWN_ON_ERROR`). Local test on synthetic data passed: eight patients with liver masks cut through the tumour (exactly their 24 patient-phases changed, 270 patients unchanged), one tumour mask on another grid (kept liver-only masking), gates 1, 2 and 4, all outputs written, the artefact-rule logic (both directions detected; one condition only and smoothing-confounded shifts refused), and the resume path (trained folds and extracted features reused). Every modified test file was restored.

## 51. E12 and E13 plans: equalized slice density, fully nested stacking (22 Oct 2026, at your request; written before either run)

**Why.** After the independent assessment (21–22 Oct), you decided to run the two experiments it named:
- **E12** tests the Ninth limitation: the models were never retrained with slice density equalized across classes. It bears on R2-3 and R4-4 (why the models fail externally) and on R2-6 (mitigation).
- **E13** quantifies the optimism of the cross-validated fusion estimates that the Fifth limitation discloses (stacking without nesting). It bears on R4-6 and R2-1.

**The main models and all main results stay unchanged, whatever E12 and E13 show.** Both are reported in full.

### E12 — retraining with slice density equalized (notebook R15, A100 with High-RAM)

**The only change to the pipeline:** before cropping, every scan is resampled along the slice axis so that its anatomical slice-density estimate equals one common target.
- The estimate is E10b's: slices containing liver ÷ largest in-plane liver width in pixels, from the scan's own liver mask.
- Factor per scan = R ÷ ratio. **R = 0.4468**, the median ratio of the 222 development patients' portal-venous scans (E10b file; no labels used). The CT is resampled linearly; masks linearly, then > 0.5 (E10's function).
- A scan with an empty liver mask uses the same patient's portal-venous ratio. If that mask is empty too, the factor is 1; those crops are black in every pipeline.
- **MCT-LTDiag:** the same rule on its primary geometry (in-plane 0.78 mm, slices kept), with the ratio from its portal-venous liver mask (the masks are registered) and one factor for all phases.
- **Everything else as in the main pipeline:**
  - liver-only masking and 96³ crops around the tumor centroid;
  - phase-dropout CNN (E3 protocol: same folds, seeds and inner validation split);
  - E2 radiomics recipe, with features re-extracted (Week 5 settings, no shape features);
  - meta-learners refitted;
  - nothing tuned.

**Gates (the notebook stops if one fails):**
1. Liver-only crops rebuilt without equalization equal the Week 2 crops (≥ 99% of patients).
2. Recomputed ratios equal E10b's per-scan values.
3. The E2 recipe reproduces the saved E2 predictions (< 1e-6), and Week 5 features re-extracted from unequalized crops of 20 patients equal the saved features (relative difference < 1e-6).
4. MCT-LTDiag primary crops equal the saved E6/E8.0 crops (≤ 1 grey level).

**Outcomes:**
- **O0, equalization check:** after equalization, class medians of the ratio and of the slice counts per phase. A slice-count-only model (multinomial logistic regression on the four log slice counts, fitted on the development set) before and after equalization: held-out macro-AUC, and out-of-fold HCC-versus-ICC AUC.
- **O1, internal:** held-out macro-AUC (bootstrap 95% CI) and out-of-fold macro-AUC of the new CNN, radiomics, CNN + radiomics and full fusion; paired bootstrap differences against the main models; per-class recall.
- **O2, residual artifact (every scan passes through the equalizing pipeline):**
  - *injection:* HCC and ICC non-contrast resampled to 0.29 × the portal-venous slice count before equalization;
  - *repair:* cHCC-CCA non-contrast resampled to the portal-venous count before equalization.
  - Each is compared with the unaltered equalized scan, using E10's thresholds (mean shift ≥ 0.05, bootstrap CI excluding 0). A smoothing control is not needed, because equalization resamples every scan. Injection measures the response to the blur of a thick reconstruction that equalization cannot remove.
- **O3, external:** MCT-LTDiag (203) HCC-versus-ICC AUC (DeLong 95% CI), paired DeLong test against the main models, sensitivity and specificity at the internal decision rule, and the confusion counts.

**What the paper will say (rules fixed now):**
- **Equalization:** it worked if, after it, the class medians of the ratio differ by at most 1.25-fold in every phase. The slice-count-only AUC after equalization is reported either way.
- **Internal:** if the held-out difference of CNN + radiomics against the main model has a bootstrap CI excluding 0, its size and direction are reported; if negative, it is described as consistent with the shortcut having inflated internal performance. Otherwise: "equalizing slice density did not measurably change internal performance".
- **External:** if the new CNN + radiomics is better on MCT-LTDiag with paired DeLong p < 0.05, the paper says that equalization improved external discrimination and gives the AUC. Otherwise it says that equalization did not improve external discrimination.
- **Residual artifact:** "the equalized CNN still responds to the thick reconstruction" only if injection meets E10's thresholds; repair is reported alongside.
- The results appear as a Results paragraph and a supplementary table. The Ninth limitation is replaced by the result, and the response letter gets a line.

### E13 — fully nested stacking evaluation (notebook R16, A100)

**Design:** for each of E7a's 5 repeats and each outer fold *k*:
- inner 4-fold stratified cross-validation of the about 178 outer-training patients (seed 1000 + 10 × repeat + *k*);
- in each inner fold, train the phase-dropout CNN (E3 protocol, inner checkpoint split as E7a) and the E2 radiomics recipe on the inner-training patients, and predict the inner-validation patients;
- fit the CNN + radiomics and full-fusion meta-learners (E2 recipe) on these inner out-of-fold predictions;
- apply them to fold *k*'s outer base predictions, which are E7a's saved out-of-fold predictions from base models trained on all outer-training patients.

That is 100 CNN trainings. Only predictions and training logs are kept; no weights.

**Gates:** the radiomics recipe on the outer folds reproduces E7a's radiomics out-of-fold predictions (< 1e-6) in every repeat; the non-nested fusion AUCs recomputed from E7a's saved predictions equal E7a's per-repeat table.

**Outcomes:**
- Per repeat, the pooled nested out-of-fold macro-AUC of CNN + radiomics and full fusion, against E7a's non-nested values.
- Optimism = non-nested − nested, as mean, SD and range over repeats.
- The nested fusion − branch differences per repeat: in how many of the 5 repeats does CNN + radiomics stay above each branch?

**What the paper will say (rules fixed now):**
- The Fifth limitation's unquantified optimism is replaced by the measured value (mean and range).
- If the mean optimism of either fusion exceeds 0.01, the nested values are reported next to the non-nested ones in Tables 2 and 3, and every cross-validation statement uses the nested value.
- The statement "better than either branch in all five repeats" is kept only if it also holds nested; otherwise it is corrected.
- Held-out results are not affected by stacking and do not change.

### Both

- **Running:** E12 (about 2–3 h) and E13 (about 5–7 h) read only existing files, write to new folders (`revision_2026-10/E12_<time>/`, `E13_<time>/`), and can run at the same time in separate Colab sessions. E13 can also be split by repeats into two parallel runs.
- **Safety:** each notebook is resumable, saves an error file and disconnects on error, and disconnects when done.

**Implementation notes (22 Oct 2026).**
- Builders and tests are kept with the private project files.
- **R16 E13**
  - Drive: `notebooks/3_revision_2026-10/1_internal_models_and_statistics/R16_E13_nested_stacking.ipynb`.
  - Local test on synthetic data (1 epoch, stand-in CNN and LightGBM) passed:
    - The gates reproduce E7a: radiomics outer folds to 1e-16, the non-nested fusions to 1e-16, and the per-repeat AUCs exactly.
    - Run as two parts (repeats 0–2 and 3–4), the second part wrote the combined five-repeat result.
    - Resuming the second part reused all 40 inner trainings.
    - The inner predictions never include the outer validation patients.
  - You started it on 22 Oct as a single session (run `E13_20261022T024552Z`, A100, repeats 0–4). The input checks and the fold gate passed.
- **R15 E12**
  - Drive: `notebooks/3_revision_2026-10/3_dataset_audit_and_explainability/R15_E12_equalized_slice_density.ipynb`.
  - Local test on synthetic data passed:
    - Gates 1, 2 and 4 hold exactly (278/278, the E10b measurements, 203/203).
    - Every scan with a liver mask is brought to R; for MCT-LTDiag this holds within ±2 slices, because the synthetic scans have only 14 slices.
    - The conditions, all outputs and the rule logic (an injected residual shift is detected) work.
  - Gate 3 can only be checked on Colab, because the local test uses a stand-in feature extractor (as for E11, whose real run gave 0.0).

## 60. Plan E14a, E14b and E15: acquisition-controlled tests and seed variability (written 23 Oct 2026, before any run)

**Why.** A blind strict review (fresh agent as Reviewer 4) recommended major revision. Its verified points include:
- M1: the external class assignments follow the slice spacing;
- M5 and Reviewer 4 comment 4: no controlled test isolates acquisition from population;
- M3(c): linear decimation is not a thick reconstruction;
- M7 and A1: CNN run-to-run variability was never measured.

You asked to run the experiments needed for a submission-ready paper, and then to finish the writing with their results. The current package was moved to (local backup folder).

**Facts fixed now from existing outputs (local, post hoc):**
- MCT-LTDiag slice-density target: median of liver slices ÷ liver width over the 203 patients (portal-venous liver mask, primary geometry, E12 file) = **R_MCT = 0.116981**.
- HCC and ICC class medians in MCT-LTDiag are 0.1167 and 0.1190 (1.02-fold), where every scan has 5 mm slices. This validates the anatomical estimator: liver proportions do not differ by class.
- Internal factors R_MCT ÷ ratio (median): HCC 0.38–0.47; ICC 0.17–0.18; cHCC-CCA 0.24–0.27 in the contrast phases and 0.91 in the non-contrast phase.

**Thickening rule (all three notebooks):** scans are made thicker only by slab averaging, because a thick reconstruction averages tissue over the slab:
- each new slice is the overlap-weighted mean of the original slices it covers;
- masks are averaged the same way, then thresholded at > 0.5;
- a scan is never made thinner, except by the linear upsampling of the smoothing controls and of E14b's small adjustments (as in E12).

### E14a: frozen main models on internal scans with MCT-like acquisition (inference only; about 1.5–2 h, L4 or A100)
- **Models and gates.** Frozen phase-dropout CNN, E2 radiomics and the CNN + radiomics meta-learner, all as in E10: development patients use their own fold model, held-out patients the 5-model ensemble. Gates A–D are E10's.
- **Condition `mct`.** Every phase of every internal scan is slab-averaged to R_MCT (factor = R_MCT ÷ the scan's own ratio, applied only if < 1). If a scan's liver mask is empty, the patient's portal-venous ratio is used; if that is empty too, the scan is left unchanged.
- **Condition `inject_slab`** (HCC and ICC): the non-contrast scan is slab-averaged to 0.29 × the portal-venous slice count, a realistic thick reconstruction. Its matched control `inject_slab_smooth` is the same slab averaging followed by linear upsampling back to the original count.
- **OA, primary statistic:** held-out HCC-versus-ICC AUC of CNN + radiomics (39 patients; score p(HCC)/[p(HCC) + p(ICC)]) with `mct` inputs against unchanged inputs, with a paired bootstrap (2,000 resamples, seed 42).
- **OA, decision rule (fixed now):** with internal 0.947 and external 0.578, the midpoint is 0.763.
  - "MCT-like acquisition alone reproduces most of the external loss" if the `mct` AUC is < 0.763 and the paired CI excludes 0.
  - "explains part of it" if the CI excludes 0 and the AUC is ≥ 0.763.
  - "does not explain it" if the CI includes 0.
- **OA, secondary:** three-class held-out macro-AUC (56), out-of-fold values (222), and predicted classes per true class for all models.
- **OC:** the E10 rules applied to `inject_slab` against `inject_slab_smooth`: shift of p(cHCC-CCA) ≥ 0.05, bootstrap CI excluding 0, control < 0.05. Only the injection direction is tested, because a thick reconstruction cannot be made thin again.

### E14b: all models retrained on internal scans with MCT-like acquisition (about 3–4 h, A100)
- **Method.** E12's notebook with two changes:
  - the target is R_MCT instead of the development median;
  - thickening uses slab averaging; thinning uses linear interpolation (as E12).
- Everything else is E12's: same folds, seeds and settings; nothing tuned. MCT-LTDiag gets the same rule (factors near 1).
- **Gates.** E12's gates, plus the recomputed MCT median ratio must equal R_MCT.
- **Rules (fixed now, as E12):**
  - harmonization succeeded if the class medians of the ratio differ at most 1.25-fold in every phase;
  - an internal change is claimed only if the held-out paired bootstrap CI excludes 0;
  - an external improvement only if the paired DeLong p < 0.05 with a higher AUC;
  - the MCT-LTDiag AUC is also compared with 0.5 (DeLong CI);
  - predicted classes are reported.
- **Interpretation (fixed now):**
  - if internal performance stays (CI includes 0) and MCT-LTDiag does not improve, acquisition geometry is not the main cause of the external failure;
  - if MCT-LTDiag improves, acquisition mismatch contributed;
  - if internal performance falls, internal discrimination depended on class-dependent acquisition.

### E15: training-seed variability of the main CNN (about 1.5–2 h, A100)
- **Method.** The phase-dropout CNN is retrained with the E3 protocol on the Week 2 crops, with the same folds and inner validation split. Only the training seed changes (initialization, data order, augmentation, dropout draws): two additional seeds, offset +1000 and +2000 per fold. CNN + radiomics meta-learners are refitted per seed on that seed's out-of-fold CNN probabilities and the saved E2 radiomics probabilities.
- **Gate.** The saved E3 phase-dropout models reproduce their saved predictions (< 0.02).
- **Outcome.** Held-out macro-AUC (56) and out-of-fold macro-AUC (222) of the CNN and of CNN + radiomics for seeds 42 (saved E3/E8b), +1000 and +2000, and their range.
- **Statement (fixed now):** the 0.013 spread of the three CNN candidates is described as "within" the seed-to-seed variability if it is no larger than the range across the three seeds, and "larger than" otherwise.

**For all three:** inputs are only read; outputs go to new folders `revision_2026-10/E14a_<time>/`, `E14b_<time>/` and `E15_<time>/`. The main models and all main results stay unchanged, whatever these show. Every result is reported.

**Additions while building the notebooks (23 Oct 2026, still before any run).** None changes a primary outcome or a rule above.
- **E14a:**
  - Added condition `mct_smooth` (secondary): the same slab averaging, then linear interpolation back to the original slice count. It separates thick-slice blur from the change in slice count.
  - OC uses only the HCC and ICC patients whose non-contrast scan was actually thickened. A scan that already has no more slices than 0.29 × portal venous is left unchanged.
  - Reported in addition, descriptively:
    - the share of the external AUC loss that MCT-like inputs reproduce, (unchanged − `mct`) ÷ (unchanged − external);
    - the same plan rule for the CNN and radiomics, each with its own midpoint;
    - tumour masks lost by the averaging;
    - three seeded evidence images.
- **E14b:**
  - Added gate 5: the recomputed MCT-LTDiag median ratio must equal R.
  - The interpretation is printed as the list of the three plan readings that apply.
  - The MCT-LTDiag AUC is compared with 0.5 by its DeLong 95% CI: better than chance only if the lower bound is > 0.5.
- **E15:**
  - Added seed offsets +3000, +4000 and +5000, for a standard deviation over six training seeds.
  - Added one retraining of seed 42 (offset 0), which measures GPU non-determinism alone.
  - Added full fusion.
  - Added gate 2: the meta-learner code reproduces the saved E8b fusions from the saved E3 models.
  - The pre-specified statement still uses only seeds 42, +1000 and +2000.
- **All three:**
  - Notebooks `R17_E14a_mct_like_acquisition_frozen_models.ipynb`, `R18_E14b_mct_density_retraining.ipynb` and `R19_E15_cnn_training_seed_variability.ipynb`.
  - On an error, each notebook saves the error to Drive and disconnects.
  - Builders and local tests are kept with the private project files.

**Reviewer points answered:**
- R4 comment 4 (acquisition versus population): E14a tests acquisition alone with frozen models; E14b retrains with the external acquisition.
- Blind-review M1 (classes follow spacing): predicted classes in E14a and E14b.
- M3(c) (a thick reconstruction is not linear decimation): slab averaging in E14a (OC) and E14b.
- M5 (no controlled test of acquisition): E14a and E14b.
- M7/A1 (run-to-run variability): E15.
- Whatever the results, they are reported in full. The three-class external question remains unanswerable (no external cHCC-CCA); the paper says so.

**Uploaded to Drive (23 Oct 2026, at your request; new files only, byte-identical to the local copies):**
- `notebooks/3_revision_2026-10/3_dataset_audit_and_explainability/R17_E14a_mct_like_acquisition_frozen_models.ipynb`
- `notebooks/3_revision_2026-10/3_dataset_audit_and_explainability/R18_E14b_mct_density_retraining.ipynb`
- `notebooks/3_revision_2026-10/1_internal_models_and_statistics/R19_E15_cnn_training_seed_variability.ipynb`
