"""Study-wide immutable ordering and shape conventions."""

CLASS_ORDER = ("HCC", "ICC", "cHCC-CCA")
PHASE_ORDER = ("P", "C1", "C2", "C3")
CROP_SIZE = 96

# CHCC is retained in column tokens for compatibility with historical artifacts;
# its display label is cHCC-CCA, the third entry in CLASS_ORDER.
FULL_FUSION_FEATURES = (
    "w4_p_HCC",
    "w4_p_ICC",
    "w4_p_CHCC",
    "w5_p_HCC",
    "w5_p_ICC",
    "w5_p_CHCC",
    "age",
    "sex",
)
