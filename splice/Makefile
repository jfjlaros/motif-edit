#
# Configuration.
#

# Reference data.
BUILD := hg38
GTF := Homo_sapiens.GRCh38.104.gtf
MOTIFS := ABEmax_strong.tsv
REFERENCE := $(BUILD).fa

# Reference data sources.
GTF_URL := http://ftp.ensembl.org/pub/release-104/gtf/homo_sapiens/$(GTF).gz
REFERENCE_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(REFERENCE).gz

# Analysis tools.
BEDTOOLS := bedtools
FASTOOLS := fastools
SKIP_EXONS := python skip_exons.py
INTERSECT_GTF:= python intersect_gtf.py
GTF_TO_CSV:= python gtf_to_csv.py

#
# Maintenance targets.
#

.PHONY: all clean distclean reference gtf
.SECONDARY:

all: $(REFERENCE) $(GTF) motif_A.raw motif_T.raw editable_exons.csv
	 

clean:
	rm -f *.raw *.bed editable_exons*

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

$(GTF):
	wget $(GTF_URL) && gunzip $@.gz

#
# Analysis targets.
#

# Find the splice sites.
skip_exons.raw: $(GTF)
	$(SKIP_EXONS) --gtf $? > $@

# Find motif sites.
motif_%.raw: $(REFERENCE) $(MOTIFS)
	$(FASTOOLS) famotif2bed $< $@ '$(shell grep -- "^$*" $(MOTIFS) | cut -f 3)'

# Sort bed files
%.bed: %.raw
	sort -k 1,1 -k 2,2n $? > $@

# Merge the motif sites
space = $(eval) $(eval)
motif_intersect.bed: motif_A.bed motif_T.bed
	sort -k 1,1 -k 2,2n -m $? > $@

# Find splice sites that are editable
editable_exons.bed: skip_exons.bed motif_intersect.bed
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

editable_exons.gtf: editable_exons.bed $(GTF)
	$(INTERSECT_GTF) --bed $< --gtf $(word 2, $^) > $@

editable_exons.csv: editable_exons.gtf
	$(GTF_TO_CSV) --gtf $< > $@
