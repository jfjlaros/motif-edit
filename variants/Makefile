#
# Configuration.
#

# Reference data.
BUILD := hg38
REFERENCE := $(BUILD).fa
MOTIFS := motifs.tsv
LOVD_VAR := LOVD_Transcript,VariantOnTranscript,VariantOnGenome_2021-04-26_14.43.16.cleaned.uniq.txt
CLIN_VAR := clinvar.db

# Reference data sources.
REFERENCE_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(REFERENCE).gz
REFSEQ_URL := ftp://hgdownload.cse.ucsc.edu/goldenPath/hg38/database/ncbiRefSeq.txt.gz

# Analysis tools.
BEDTOOLS := bedtools
FASTOOLS := fastools
LOVD_TO_RAW := python lovd_to_raw.py


#
# Maintenance targets.
#

.PHONY: all clean distclean reference
.SECONDARY:

all: motif_C.bed motif_G.bed \
     lovd_C.bed clinvar_C.vcf lovd_G.bed clinvar_G.vcf \
     intersect_lovd_C.bed intersect_lovd_G.bed \
     intersect_clinvar_C.bed intersect_clinvar_G.bed

clean:
	rm -f *.mtf *.raw *.bed *.vcf

distclean: clean
	rm -f $(REFERENCE)

# Location of reference data.
reference:
	@echo "$(REFERENCE_URL)\n$(ANNOTATION_URL)"


#
# Reference data download targets.
#

$(REFERENCE):
	wget $(REFERENCE_URL) && gunzip $@.gz


#
# Analysis targets.
#

# Add a header to a BED file.
%.bed: %.raw
	echo 'track name=$*' > $@ && sort -k 1,1 -k 2,2n -u $< >> $@

sum_%.raw: intersect_lovd_%.raw intersect_clinvar_%.raw
	cat $^ > $@

intersect_lovd_%.raw: motif_%.raw lovd_%.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

intersect_clinvar_%.raw: motif_%.raw clinvar_%.vcf
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

# Find motif sites.
motif_%.raw: $(REFERENCE) $(MOTIFS)
	$(FASTOOLS) famotif2bed $< $@ '$(shell grep -- "^$*" $(MOTIFS) | cut -f 3)'

# Find variants in LOVD.
lovd_%.raw: $(LOVD_VAR)
	$(LOVD_TO_RAW) -o $@ $< $(shell grep -- "^$*" $(MOTIFS) | cut -f 1-2)

# Find variants in ClinVar.
clinvar_%.vcf: $(CLIN_VAR)
	grep '^#' $(CLIN_VAR) > $@ && grep -v '^#' $< | sed 's/^/chr/' | \
    grep '^\S*	\S*	\S*	$(shell grep -- "^$*" $(MOTIFS) | cut -f 1-2)	.*\(Likely_p\|P\)athogenic' >> $@
